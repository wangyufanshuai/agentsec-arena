from __future__ import annotations

from .models import AgentStep, Finding, Report, Run, Scenario, Score, SecurityEvent


def render_markdown_report(
    run: Run,
    scenario: Scenario,
    steps: list[AgentStep],
    events: list[SecurityEvent],
    findings: list[Finding],
    score: Score,
) -> Report:
    lines: list[str] = [
        f"# AgentSec Arena Report: {scenario.name}",
        "",
        "## Safety Boundary",
        "This round was constrained to the local Docker cyber range. Real websites, public IPs, host networking, and Docker socket access are out of scope.",
        "",
        "## Scenario",
        f"- Scenario: {scenario.name}",
        f"- Type: {scenario.type.value}",
        f"- Run ID: `{run.id}`",
        f"- Network: `{run.network_name}`",
        f"- Target: `{run.mapped_target_url}`",
        "",
        "## Score",
        f"- Attacker: {score.attacker}",
        f"- Defender: {score.defender}",
        f"- Safety: {score.safety}",
        f"- Total: {score.total}",
        "",
        "## Findings",
    ]

    if not findings:
        lines.append("- No validated findings were recorded.")
    for finding in findings:
        lines.extend(
            [
                f"- **{finding.title}** ({finding.severity.value})",
                f"  - Target: `{finding.affected_target}`",
                f"  - Evidence: {finding.evidence}",
                f"  - OWASP: {', '.join(finding.owasp) or 'n/a'}",
                f"  - CWE: {', '.join(finding.cwe) or 'n/a'}",
                f"  - ATT&CK: {', '.join(finding.attack) or 'n/a'}",
            ]
        )

    lines.extend(["", "## Agent Timeline"])
    if not steps:
        lines.append("- No agent steps were recorded.")
    for step in steps:
        tool = f" via `{step.tool_call.tool}`" if step.tool_call else ""
        lines.append(f"- `{step.agent.value}` {step.action}{tool}: {step.output_summary}")

    lines.extend(["", "## Security Events"])
    if not events:
        lines.append("- No security events were recorded.")
    for event in events:
        lines.append(f"- [{event.severity.value}] `{event.source}` {event.event_type}: {event.message}")

    lines.extend(["", "## Mitigation Notes"])
    lines.append("- Keep attacker tooling inside the current Docker network allowlist.")
    lines.append("- Convert defender recommendations into detection queries before enabling automated blocking.")
    lines.append("- Patch vulnerable training targets only in derived images so baseline scenarios remain reproducible.")

    return Report(
        run_id=run.id,
        title=f"AgentSec Arena Report - {scenario.name}",
        content="\n".join(lines),
    )

