from __future__ import annotations

import csv
import importlib.util
import sys
from functools import lru_cache
from pathlib import Path
from typing import Any


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


@lru_cache(maxsize=1)
def _feature_module():
    module_path = (
        _repo_root()
        / "singpass-login-risk-engine"
        / "feature_engineering"
        / "src"
        / "generate_login_features.py"
    )
    spec = importlib.util.spec_from_file_location("login_feature_builder_module", module_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load login feature builder module from {module_path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


@lru_cache(maxsize=1)
def _raw_event_map() -> dict[str, dict[str, str]]:
    events_path = _repo_root() / "data" / "input_data" / "generated" / "events.csv"
    with events_path.open(newline="") as f:
        return {row["event_id"]: row for row in csv.DictReader(f)}


@lru_cache(maxsize=1)
def _feature_map() -> dict[str, dict[str, Any]]:
    module = _feature_module()
    rows, _ = module.build_login_features()
    return {row["event_id"]: row for row in rows}


def build_features_from_event_id(event_id: str) -> dict[str, Any] | None:
    raw_event = _raw_event_map().get(event_id)
    if raw_event is None:
        return None
    if raw_event["event_type"] not in {"app_login_success", "qr_login_approved"}:
        return None
    return _feature_map().get(event_id)
