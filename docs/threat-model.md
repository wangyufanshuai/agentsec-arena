# Threat Model

## Assets

- User machine and local files.
- Docker daemon and Docker networks.
- API state, reports, and logs.
- LLM prompts and tool outputs.

## Trust Boundaries

- Browser to API.
- API to worker.
- Worker to Docker daemon.
- Agent runtime to tool gateway.
- Target containers to observability stack.

## Primary Abuse Paths

- Prompt injection causing an agent to scan a real website.
- Tool command injection requesting host network or Docker socket access.
- Scenario template adding unsafe host mounts.
- Report generation leaking sensitive local paths or environment variables.

## Mitigations

- Tool target allowlist before execution.
- No Docker socket inside attacker containers.
- No host network for target or attacker containers.
- Internal Docker networks for lab targets.
- Non-root attacker containers and dropped capabilities in future real tool images.
- Structured audit log for every allowed and denied tool call.

