from __future__ import annotations

import json
from pathlib import Path

from .models import Scenario, ScenarioCreate


REPO_ROOT = Path(__file__).resolve().parents[3]
SCENARIO_ROOT = REPO_ROOT / "infra" / "scenarios"


class ScenarioCatalog:
    def __init__(self) -> None:
        self._scenarios: dict[str, Scenario] = {}
        self.reload()

    def reload(self) -> None:
        loaded: dict[str, Scenario] = {}
        for file in SCENARIO_ROOT.glob("**/scenario.json"):
            data = json.loads(file.read_text(encoding="utf-8"))
            loaded[data["id"]] = Scenario(**data)
        self._scenarios = loaded

    def list(self) -> list[Scenario]:
        return sorted(self._scenarios.values(), key=lambda item: item.id)

    def get(self, scenario_id: str) -> Scenario:
        return self._scenarios[scenario_id]

    def add(self, payload: ScenarioCreate) -> Scenario:
        scenario = Scenario(
            **payload.model_dump(),
            default_credentials={},
            healthcheck={},
            owasp=[],
            cwe=[],
            attack=[],
            log_sources=[],
            scoring={},
        )
        self._scenarios[scenario.id] = scenario
        return scenario

