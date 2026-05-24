# AgentSec Arena

AgentSec Arena is a local-only AI cyber range for defensive evaluation. It orchestrates intentionally vulnerable Docker targets, runs constrained attacker and defender agents, scores each round, and produces an evidence-backed report.

> Safety boundary: this project is for local, authorized lab targets only. It must not scan real websites or public IP ranges. Attacker tools are routed through a guard that only allows the current Docker range network, registered service names, and explicitly mapped localhost target ports.

## MVP Capabilities

- Scenario catalog for DVWA, OWASP Juice Shop, and three Vulhub-style starter scenarios.
- FastAPI backend with run lifecycle, event stream, mock attacker, mock defender, scoring, and Markdown reports.
- Next.js dashboard for scenarios, active runs, logs, scores, ATT&CK mapping, findings, and reports.
- Tool gateway safety checks for host allowlisting, cloud metadata blocking, Docker socket blocking, host network blocking, and public target blocking.
- Docker Compose stubs for app services, observability, and vulnerable target templates.
- Unit tests for safety policy, scoring, report rendering, scenario loading, and API flow.

## Quick Start

Backend:

```powershell
cd E:\xuexi\agentsec-arena\apps\api
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e . pytest httpx
pytest
uvicorn agentsec_arena.main:app --reload --port 8000
```

Frontend:

```powershell
cd E:\xuexi\agentsec-arena\apps\web
npm install
npm run dev
```

Open `http://localhost:3000`. The frontend expects the API at `http://localhost:8000` unless `NEXT_PUBLIC_API_BASE` is set.

## Repository Layout

```text
apps/api                  FastAPI backend
apps/web                  Next.js dashboard
packages/agent-runtime    Agent abstraction notes and package placeholder
packages/tool-gateway     Safety gateway package placeholder
packages/scoring          Scoring package placeholder
packages/reports          Report package placeholder
infra/compose             App and observability compose files
infra/scenarios           Scenario metadata and target compose templates
workers                   Worker entrypoints for future async execution
docs                      Safety, threat model, scenario authoring
```

## Current Security Model

The MVP uses mock agents and deliberately conservative safety checks. Real tool execution should only be added behind `ToolGateway.validate_target` and command allowlists. Attacker containers must never receive the Docker socket, host networking, or broad host mounts.

