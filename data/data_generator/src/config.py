from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class GeneratorConfig:
    random_seed: int
    num_users: int
    avg_devices_per_user: float
    num_services: int
    avg_sessions_per_user: int
    fraud_session_ratio: float
    legit_unusual_session_ratio: float
    scenario_weights: dict[str, float]


def load_config(config_path: str | Path) -> GeneratorConfig:
    path = Path(config_path)
    raw = json.loads(path.read_text())
    return GeneratorConfig(**raw)
