export type Scenario = {
  id: string;
  name: string;
  type: "dvwa" | "juice-shop" | "vulhub";
  description: string;
  compose_file: string;
  service_name: string;
  internal_url: string;
  mapped_url: string;
  default_credentials: Record<string, string>;
  healthcheck: Record<string, unknown>;
  tags: string[];
  owasp: string[];
  cwe: string[];
  attack: string[];
  log_sources: string[];
  scoring: Record<string, unknown>;
};

export type RunStatus =
  | "queued"
  | "running"
  | "attacker_complete"
  | "defender_complete"
  | "completed"
  | "stopped"
  | "safety_violation"
  | "failed";

export type Run = {
  id: string;
  scenario_id: string;
  status: RunStatus;
  network_name: string;
  difficulty: string;
  enable_logs: boolean;
  allowlist_hosts: string[];
  mapped_target_url: string;
  created_at: string;
  updated_at: string;
  started_at: string | null;
  ended_at: string | null;
  containers: Array<{
    name: string;
    image: string;
    role: "target" | "attacker" | "defender" | "observability";
    status: "created" | "running" | "stopped" | "failed";
    ports: string[];
  }>;
};

export type AgentStep = {
  id: string;
  run_id: string;
  agent: "attacker" | "defender";
  action: string;
  input_summary: string;
  output_summary: string;
  status: "allowed" | "denied" | "completed" | "failed";
  created_at: string;
  tool_call?: {
    tool: string;
    target: string;
    allowed: boolean;
    reason: string;
    stdout_summary: string;
    stderr_summary: string;
    duration_ms: number;
  } | null;
};

export type SecurityEvent = {
  id: string;
  run_id: string;
  source: string;
  event_type: string;
  severity: "info" | "low" | "medium" | "high" | "critical";
  message: string;
  labels: Record<string, string>;
  created_at: string;
};

export type Finding = {
  id: string;
  run_id: string;
  title: string;
  severity: "info" | "low" | "medium" | "high" | "critical";
  evidence: string;
  affected_target: string;
  owasp: string[];
  cwe: string[];
  attack: string[];
  created_at: string;
};

export type Score = {
  run_id: string;
  attacker: number;
  defender: number;
  safety: number;
  total: number;
  rationale: string[];
  updated_at: string;
};

export type Report = {
  id: string;
  run_id: string;
  format: "markdown" | "html";
  title: string;
  content: string;
  created_at: string;
};

export type RunBundle = {
  run: Run;
  scenario: Scenario;
  events: SecurityEvent[];
  steps: AgentStep[];
  findings: Finding[];
  score?: Score | null;
};

