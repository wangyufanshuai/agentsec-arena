from __future__ import annotations

from urllib.parse import urlparse

from .models import AgentKind, AgentStep, Finding, Run, RunStatus, Scenario, SecurityEvent, Severity, ToolCall, utc_now
from .safety import ToolGateway
from .store import MemoryStore


def _localhost_ports(run: Run) -> set[int]:
    parsed = urlparse(run.mapped_target_url)
    if parsed.port:
        return {parsed.port}
    if parsed.scheme == "http":
        return {80}
    if parsed.scheme == "https":
        return {443}
    return set()


def build_gateway(run: Run) -> ToolGateway:
    return ToolGateway(
        allowlist_hosts=set(host.lower() for host in run.allowlist_hosts),
        allow_localhost_ports=_localhost_ports(run),
    )


def run_mock_attacker(store: MemoryStore, run: Run, scenario: Scenario) -> Run:
    gateway = build_gateway(run)
    targets = [
        scenario.internal_url,
        f"{scenario.internal_url}/login.php",
    ]

    for target in targets:
        decision = gateway.validate_target(target)
        tool_call = ToolCall(
            tool="http_probe",
            target=target,
            allowed=decision.allowed,
            reason=decision.reason,
            stdout_summary="HTTP 200 and form markers observed" if decision.allowed else "",
            stderr_summary="" if decision.allowed else decision.reason,
            duration_ms=120,
        )
        step = AgentStep(
            run_id=run.id,
            agent=AgentKind.attacker,
            action="probe_target",
            input_summary=f"Probe {target}",
            output_summary=tool_call.stdout_summary or f"Denied: {decision.reason}",
            status="allowed" if decision.allowed else "denied",
            tool_call=tool_call,
        )
        store.add_step(step)

        store.add_event(
            SecurityEvent(
                run_id=run.id,
                source="attacker",
                event_type="tool_call",
                severity=Severity.info if decision.allowed else Severity.high,
                message=f"{tool_call.tool} -> {target}: {decision.reason}",
                labels={"allowed": str(decision.allowed).lower(), "target": decision.normalized_target},
            )
        )

        if not decision.allowed and decision.violation_level == "high":
            run.status = RunStatus.safety_violation
            run.ended_at = utc_now()
            store.update_run(run)
            store.add_event(
                SecurityEvent(
                    run_id=run.id,
                    source="safety_guard",
                    event_type="safety_violation",
                    severity=Severity.high,
                    message=f"Out-of-scope target denied: {target}",
                    labels={"target": decision.normalized_target},
                )
            )
            return run

    finding = Finding(
        run_id=run.id,
        title=f"{scenario.name} exposes intentionally vulnerable training routes",
        severity=Severity.medium,
        evidence="Mock attacker observed login/form endpoints and scenario metadata indicates vulnerable lab behavior.",
        affected_target=scenario.internal_url,
        owasp=scenario.owasp,
        cwe=scenario.cwe,
        attack=scenario.attack,
    )
    store.add_finding(finding)
    run.status = RunStatus.attacker_complete
    store.update_run(run)
    return run


def run_mock_defender(store: MemoryStore, run: Run, scenario: Scenario) -> Run:
    store.add_step(
        AgentStep(
            run_id=run.id,
            agent=AgentKind.defender,
            action="analyze_logs",
            input_summary="Review attacker tool calls, container logs, and scenario metadata.",
            output_summary="Detected route probing and generated containment plus patch guidance.",
            status="completed",
        )
    )
    store.add_event(
        SecurityEvent(
            run_id=run.id,
            source="defender",
            event_type="detection",
            severity=Severity.medium,
            message="Route probing pattern detected against local vulnerable target.",
            labels={"query": '{run_id="' + run.id + '", source="attacker"}'},
        )
    )
    store.add_event(
        SecurityEvent(
            run_id=run.id,
            source="defender",
            event_type="mitigation",
            severity=Severity.info,
            message="Recommend blocking attacker container identity for the run and adding input validation/WAF rules.",
            labels={"scenario": scenario.id},
        )
    )

    if run.status != RunStatus.safety_violation:
        run.status = RunStatus.defender_complete
    store.update_run(run)
    return run
