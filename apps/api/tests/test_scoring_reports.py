from agentsec_arena.models import AgentKind, AgentStep, Finding, Run, Scenario, ScenarioType, Severity, ToolCall
from agentsec_arena.reports import render_markdown_report
from agentsec_arena.scoring import calculate_score


def test_score_rewards_findings_and_safety():
    run = Run(
        scenario_id="dvwa",
        network_name="agentsec_run_test",
        allowlist_hosts=["dvwa"],
        mapped_target_url="http://localhost:8081",
    )
    steps = [
        AgentStep(
            run_id=run.id,
            agent=AgentKind.attacker,
            action="probe",
            input_summary="probe dvwa",
            output_summary="ok",
            tool_call=ToolCall(tool="http_probe", target="http://dvwa", allowed=True, reason="allowed"),
        )
    ]
    findings = [
        Finding(
            run_id=run.id,
            title="Training finding",
            severity=Severity.medium,
            evidence="evidence",
            affected_target="http://dvwa",
        )
    ]
    score = calculate_score(run, steps, findings, [])
    assert score.attacker > 0
    assert score.safety == 100
    assert score.total > 0


def test_report_contains_score_and_findings():
    scenario = Scenario(
        id="dvwa",
        name="DVWA Local Range",
        type=ScenarioType.dvwa,
        description="test",
        compose_file="compose.yml",
        service_name="dvwa",
        internal_url="http://dvwa",
        mapped_url="http://localhost:8081",
    )
    run = Run(
        scenario_id="dvwa",
        network_name="agentsec_run_test",
        allowlist_hosts=["dvwa"],
        mapped_target_url="http://localhost:8081",
    )
    finding = Finding(
        run_id=run.id,
        title="Training finding",
        severity=Severity.medium,
        evidence="evidence",
        affected_target="http://dvwa",
    )
    score = calculate_score(run, [], [finding], [])
    report = render_markdown_report(run, scenario, [], [], [finding], score)
    assert "AgentSec Arena Report" in report.content
    assert "Training finding" in report.content
    assert "Safety Boundary" in report.content

