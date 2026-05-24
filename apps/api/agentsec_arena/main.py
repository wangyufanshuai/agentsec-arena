from __future__ import annotations

from datetime import timezone

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from .agents import run_mock_attacker, run_mock_defender
from .models import ContainerState, Run, RunBundle, RunCreate, RunStatus, Scenario, ScenarioCreate, SecurityEvent, Severity, utc_now
from .reports import render_markdown_report
from .scenarios import ScenarioCatalog
from .scoring import calculate_score
from .store import MemoryStore


app = FastAPI(title="AgentSec Arena API", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

catalog = ScenarioCatalog()
store = MemoryStore()


def get_run_or_404(run_id: str) -> Run:
    try:
        return store.runs[run_id]
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="run not found") from exc


def get_scenario_or_404(scenario_id: str) -> Scenario:
    try:
        return catalog.get(scenario_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="scenario not found") from exc


def bundle(run: Run) -> RunBundle:
    scenario = get_scenario_or_404(run.scenario_id)
    return RunBundle(
        run=run,
        scenario=scenario,
        events=store.events.get(run.id, []),
        steps=store.steps.get(run.id, []),
        findings=store.findings.get(run.id, []),
        score=store.scores.get(run.id),
    )


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "agentsec-arena-api"}


@app.get("/api/scenarios", response_model=list[Scenario])
def list_scenarios() -> list[Scenario]:
    return catalog.list()


@app.post("/api/scenarios", response_model=Scenario, status_code=201)
def create_scenario(payload: ScenarioCreate) -> Scenario:
    return catalog.add(payload)


@app.get("/api/runs", response_model=list[RunBundle])
def list_runs() -> list[RunBundle]:
    return [bundle(run) for run in sorted(store.runs.values(), key=lambda item: item.created_at, reverse=True)]


@app.post("/api/runs", response_model=RunBundle, status_code=201)
def create_run(payload: RunCreate) -> RunBundle:
    scenario = get_scenario_or_404(payload.scenario_id)
    run = Run(
        scenario_id=scenario.id,
        network_name="pending",
        difficulty=payload.difficulty,
        enable_logs=payload.enable_logs,
        allowlist_hosts=[scenario.service_name, scenario.service_name.lower()],
        mapped_target_url=scenario.mapped_url,
        containers=[
            ContainerState(
                name=f"{scenario.service_name}-target",
                image=scenario.compose_file,
                role="target",
                status="running",
                ports=[scenario.mapped_url],
            ),
            ContainerState(name="agentsec-attacker", image="agentsec/attacker:mock", role="attacker", status="created"),
            ContainerState(name="agentsec-defender", image="agentsec/defender:mock", role="defender", status="created"),
        ],
    )
    run.network_name = f"agentsec_run_{run.id[:8]}"
    run.status = RunStatus.running
    run.started_at = utc_now()
    store.add_run(run)
    store.add_event(
        SecurityEvent(
            run_id=run.id,
            source="orchestrator",
            event_type="run_started",
            severity=Severity.info,
            message=f"Started local-only scenario {scenario.name} in Docker network {run.network_name}.",
            labels={"scenario": scenario.id, "network": run.network_name},
        )
    )
    return bundle(run)


@app.get("/api/runs/{run_id}", response_model=RunBundle)
def get_run(run_id: str) -> RunBundle:
    return bundle(get_run_or_404(run_id))


@app.post("/api/runs/{run_id}/stop", response_model=RunBundle)
def stop_run(run_id: str) -> RunBundle:
    run = get_run_or_404(run_id)
    run.status = RunStatus.stopped
    run.ended_at = utc_now()
    for container in run.containers:
        container.status = "stopped"
    store.update_run(run)
    store.add_event(
        SecurityEvent(
            run_id=run.id,
            source="orchestrator",
            event_type="run_stopped",
            severity=Severity.info,
            message="Stopped local run and marked all containers stopped.",
        )
    )
    return bundle(run)


@app.post("/api/runs/{run_id}/start-attacker", response_model=RunBundle)
def start_attacker(run_id: str) -> RunBundle:
    run = get_run_or_404(run_id)
    scenario = get_scenario_or_404(run.scenario_id)
    run = run_mock_attacker(store, run, scenario)
    score = calculate_score(run, store.steps[run.id], store.findings[run.id], store.events[run.id])
    store.set_score(score)
    return bundle(run)


@app.post("/api/runs/{run_id}/start-defender", response_model=RunBundle)
def start_defender(run_id: str) -> RunBundle:
    run = get_run_or_404(run_id)
    scenario = get_scenario_or_404(run.scenario_id)
    run = run_mock_defender(store, run, scenario)
    if run.status == RunStatus.defender_complete:
        run.status = RunStatus.completed
        run.ended_at = utc_now()
        store.update_run(run)
    score = calculate_score(run, store.steps[run.id], store.findings[run.id], store.events[run.id])
    store.set_score(score)
    return bundle(run)


@app.get("/api/runs/{run_id}/events", response_model=list[SecurityEvent])
def get_events(run_id: str) -> list[SecurityEvent]:
    get_run_or_404(run_id)
    return store.events.get(run_id, [])


@app.get("/api/runs/{run_id}/score")
def get_score(run_id: str):
    run = get_run_or_404(run_id)
    score = store.scores.get(run_id)
    if score is None:
        score = calculate_score(run, store.steps.get(run_id, []), store.findings.get(run_id, []), store.events.get(run_id, []))
        store.set_score(score)
    return score


@app.post("/api/runs/{run_id}/report", status_code=201)
def create_report(run_id: str):
    run = get_run_or_404(run_id)
    scenario = get_scenario_or_404(run.scenario_id)
    score = store.scores.get(run_id) or calculate_score(
        run,
        store.steps.get(run_id, []),
        store.findings.get(run_id, []),
        store.events.get(run_id, []),
    )
    store.set_score(score)
    report = render_markdown_report(
        run,
        scenario,
        store.steps.get(run_id, []),
        store.events.get(run_id, []),
        store.findings.get(run_id, []),
        score,
    )
    store.add_report(report)
    return report


@app.get("/api/reports/{report_id}")
def get_report(report_id: str):
    try:
        return store.reports[report_id]
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="report not found") from exc

