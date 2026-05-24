from __future__ import annotations

from .models import AgentStep, Finding, Report, Run, Score, SecurityEvent, utc_now


class MemoryStore:
    def __init__(self) -> None:
        self.runs: dict[str, Run] = {}
        self.steps: dict[str, list[AgentStep]] = {}
        self.events: dict[str, list[SecurityEvent]] = {}
        self.findings: dict[str, list[Finding]] = {}
        self.scores: dict[str, Score] = {}
        self.reports: dict[str, Report] = {}

    def add_run(self, run: Run) -> Run:
        self.runs[run.id] = run
        self.steps[run.id] = []
        self.events[run.id] = []
        self.findings[run.id] = []
        return run

    def update_run(self, run: Run) -> Run:
        run.updated_at = utc_now()
        self.runs[run.id] = run
        return run

    def add_event(self, event: SecurityEvent) -> SecurityEvent:
        self.events.setdefault(event.run_id, []).append(event)
        return event

    def add_step(self, step: AgentStep) -> AgentStep:
        self.steps.setdefault(step.run_id, []).append(step)
        return step

    def add_finding(self, finding: Finding) -> Finding:
        self.findings.setdefault(finding.run_id, []).append(finding)
        return finding

    def set_score(self, score: Score) -> Score:
        self.scores[score.run_id] = score
        return score

    def add_report(self, report: Report) -> Report:
        self.reports[report.id] = report
        return report

