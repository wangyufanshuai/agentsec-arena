# Scenario Authoring

Each scenario has a `scenario.json` file and an optional Docker Compose template.

Required fields:

- `id`
- `name`
- `type`
- `description`
- `compose_file`
- `service_name`
- `internal_url`
- `mapped_url`

Recommended metadata:

- `default_credentials`
- `healthcheck`
- `tags`
- `owasp`
- `cwe`
- `attack`
- `log_sources`
- `scoring`

Rules:

- Use local vulnerable apps only.
- Do not use host networking.
- Do not mount the Docker socket.
- Keep target service names stable because the tool gateway allowlist depends on them.
- Assign mapped ports that do not conflict with the API, frontend, or Grafana.

