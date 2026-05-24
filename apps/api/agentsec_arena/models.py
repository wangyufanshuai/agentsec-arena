from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Literal
from uuid import uuid4

from pydantic import BaseModel, Field, HttpUrl


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class ScenarioType(str, Enum):
    dvwa = "dvwa"
    juice_shop = "juice-shop"
    vulhub = "vulhub"


class RunStatus(str, Enum):
    queued = "queued"
    running = "running"
    attacker_complete = "attacker_complete"
    defender_complete = "defender_complete"
    completed = "completed"
    stopped = "stopped"
    safety_violation = "safety_violation"
    failed = "failed"


class AgentKind(str, Enum):
    attacker = "attacker"
    defender = "defender"


class Severity(str, Enum):
    info = "info"
    low = "low"
    medium = "medium"
    high = "high"
    critical = "critical"


class Scenario(BaseModel):
    id: str
    name: str
    type: ScenarioType
    description: str
    compose_file: str
    service_name: str
    internal_url: str
    mapped_url: str
    default_credentials: dict[str, str] = Field(default_factory=dict)
    healthcheck: dict[str, Any] = Field(default_factory=dict)
    tags: list[str] = Field(default_factory=list)
    owasp: list[str] = Field(default_factory=list)
    cwe: list[str] = Field(default_factory=list)
    attack: list[str] = Field(default_factory=list)
    log_sources: list[str] = Field(default_factory=list)
    scoring: dict[str, Any] = Field(default_factory=dict)


class ScenarioCreate(BaseModel):
    id: str
    name: str
    type: ScenarioType
    description: str
    compose_file: str
    service_name: str
    internal_url: str
    mapped_url: str
    tags: list[str] = Field(default_factory=list)


class RunCreate(BaseModel):
    scenario_id: str
    difficulty: Literal["training", "standard", "hard"] = "training"
    enable_logs: bool = True


class ContainerState(BaseModel):
    name: str
    image: str
    role: Literal["target", "attacker", "defender", "observability"]
    status: Literal["created", "running", "stopped", "failed"] = "created"
    ports: list[str] = Field(default_factory=list)


class Run(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    scenario_id: str
    status: RunStatus = RunStatus.queued
    network_name: str
    difficulty: str = "training"
    enable_logs: bool = True
    allowlist_hosts: list[str] = Field(default_factory=list)
    mapped_target_url: str
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)
    started_at: datetime | None = None
    ended_at: datetime | None = None
    containers: list[ContainerState] = Field(default_factory=list)


class ToolCall(BaseModel):
    tool: str
    target: str
    allowed: bool
    reason: str
    stdout_summary: str = ""
    stderr_summary: str = ""
    duration_ms: int = 0


class AgentStep(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    run_id: str
    agent: AgentKind
    action: str
    input_summary: str
    output_summary: str
    status: Literal["allowed", "denied", "completed", "failed"] = "completed"
    tool_call: ToolCall | None = None
    created_at: datetime = Field(default_factory=utc_now)


class SecurityEvent(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    run_id: str
    source: str
    event_type: str
    severity: Severity = Severity.info
    message: str
    labels: dict[str, str] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=utc_now)


class Finding(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    run_id: str
    title: str
    severity: Severity
    evidence: str
    affected_target: str
    owasp: list[str] = Field(default_factory=list)
    cwe: list[str] = Field(default_factory=list)
    attack: list[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=utc_now)


class Score(BaseModel):
    run_id: str
    attacker: int = 0
    defender: int = 0
    safety: int = 100
    total: int = 0
    rationale: list[str] = Field(default_factory=list)
    updated_at: datetime = Field(default_factory=utc_now)


class Report(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    run_id: str
    format: Literal["markdown", "html"] = "markdown"
    title: str
    content: str
    created_at: datetime = Field(default_factory=utc_now)


class RunBundle(BaseModel):
    run: Run
    scenario: Scenario
    events: list[SecurityEvent] = Field(default_factory=list)
    steps: list[AgentStep] = Field(default_factory=list)
    findings: list[Finding] = Field(default_factory=list)
    score: Score | None = None


class SafetyDecision(BaseModel):
    allowed: bool
    reason: str
    normalized_target: str
    violation_level: Literal["none", "low", "high"] = "none"

