# Orchestrator Worker

Future worker responsible for Docker lifecycle operations:

- create run network
- render scenario compose
- start target containers
- start constrained attacker/defender containers
- collect container status
- tear down run resources

The MVP keeps orchestration synchronous in the API to avoid requiring Redis during local development.

