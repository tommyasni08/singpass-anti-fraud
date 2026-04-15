from __future__ import annotations

import json
from functools import lru_cache
from typing import Any

import joblib
import pandas as pd

from . import config
from .session_score_features import build_features_from_event_id


@lru_cache(maxsize=1)
def _session_metadata() -> dict[str, Any]:
    path = config.session_ml_dir() / "serving_metadata.json"
    return json.loads(path.read_text())


@lru_cache(maxsize=1)
def _session_pipeline():
    return joblib.load(config.session_ml_dir() / "serving_pipeline.joblib")


def metadata() -> dict[str, Any]:
    meta = _session_metadata()
    return {
        "scoring_name": "session_score",
        "entity_key": "session_id",
        "numeric_features": meta["numeric_features"],
        "categorical_features": meta["categorical_features"],
        "notes": [
            "This endpoint accepts model-ready session features.",
            "Use the event-triggered session route to build session features from a raw post-login event by event_id.",
            "The API returns rule, ML, and hybrid outputs together.",
            "The current hybrid policy prioritizes containment recall.",
        ],
    }


def _to_int(value: Any) -> int:
    if value in {"", None}:
        return 0
    return int(float(value))


RULE_WEIGHTS = {
    "R01_consent_granted_in_session": 3,
    "R02_signing_completed_in_session": 3,
    "R03_stacked_sensitive_activity": 3,
    "R04_sensitive_session_with_service_switching": 2,
    "R05_sensitive_session_without_benign_usage": 2,
    "R06_high_burst_sensitive_session": 2,
    "R07_first_time_sensitive_flow": 1,
}


def _evaluate_rules(row: dict[str, Any]) -> list[str]:
    triggered: list[str] = []
    if _to_int(row.get("has_any_consent_granted_flag")) == 1:
        triggered.append("R01_consent_granted_in_session")
    if _to_int(row.get("has_any_sign_completed_flag")) == 1:
        triggered.append("R02_signing_completed_in_session")
    if _to_int(row.get("sensitive_event_after_sensitive_event_flag")) == 1:
        triggered.append("R03_stacked_sensitive_activity")
    if (
        _to_int(row.get("sensitive_event_count")) >= 1
        and _to_int(row.get("service_switch_count")) >= 1
        and _to_int(row.get("benign_service_usage_count")) == 0
    ):
        triggered.append("R04_sensitive_session_with_service_switching")
    if _to_int(row.get("sensitive_event_count")) >= 1 and _to_int(row.get("benign_service_usage_count")) == 0:
        triggered.append("R05_sensitive_session_without_benign_usage")
    if _to_int(row.get("sensitive_event_count")) >= 1 and _to_int(row.get("post_login_duration_seconds")) <= 60:
        triggered.append("R06_high_burst_sensitive_session")
    if (
        _to_int(row.get("first_time_consent_flow_for_user_flag")) == 1
        or _to_int(row.get("first_time_sign_flow_for_user_flag")) == 1
    ):
        triggered.append("R07_first_time_sensitive_flow")
    return triggered


def _rule_band(score: int) -> str:
    if score >= 5:
        return "critical"
    if score >= 3:
        return "high"
    if score >= 1:
        return "medium"
    return "low"


def _hybrid_policy(rule_band: str, rule_review_flag: int, ml_score: float) -> tuple[str, str, int]:
    if rule_band == "critical":
        return "critical", "restrict_or_manual_review", 1
    if rule_review_flag == 1:
        return "high", "manual_review", 1
    if ml_score >= 0.3:
        return "medium", "review_due_to_behavioral_risk", 1
    return "low", "allow", 0


def _prepare_frame(features: dict[str, Any]) -> pd.DataFrame:
    meta = _session_metadata()
    row: dict[str, Any] = {}
    for col in meta["numeric_features"]:
        value = features.get(col, 0)
        row[col] = 0 if value in {"", None} else float(value)
    for col in meta["categorical_features"]:
        value = features.get(col, "unknown")
        row[col] = "unknown" if value in {"", None} else str(value)
    return pd.DataFrame([row])


def _explanations(triggered_rules: list[str], ml_score: float, hybrid_action: str) -> list[str]:
    out = []
    if triggered_rules:
        out.append(f"Triggered rules: {', '.join(triggered_rules)}")
    if ml_score >= 0.5:
        out.append("ML score is in the strong behavioural-risk range.")
    elif ml_score >= 0.3:
        out.append("ML score crossed the recall-first review threshold.")
    out.append(f"Hybrid action selected: {hybrid_action}")
    return out


def score(features: dict[str, Any]) -> dict[str, Any]:
    session_id = str(features.get("session_id") or "session_score_request")
    triggered_rules = _evaluate_rules(features)
    rule_score = sum(RULE_WEIGHTS[name] for name in triggered_rules)
    rule_risk_band = _rule_band(rule_score)
    rule_review_flag = 1 if rule_score >= 3 else 0

    frame = _prepare_frame(features)
    ml_score = float(_session_pipeline().predict_proba(frame)[0][1])
    hybrid_risk_band, hybrid_action, hybrid_review_flag = _hybrid_policy(rule_risk_band, rule_review_flag, ml_score)

    return {
        "scoring_name": "session_score",
        "entity_id": session_id,
        "rule_score": rule_score,
        "rule_risk_band": rule_risk_band,
        "triggered_rules": triggered_rules,
        "ml_score": ml_score,
        "hybrid_risk_band": hybrid_risk_band,
        "hybrid_action": hybrid_action,
        "hybrid_review_flag": hybrid_review_flag,
        "explanations": _explanations(triggered_rules, ml_score, hybrid_action),
    }


def score_from_session_id(session_id: str) -> dict[str, Any] | None:
    path = config.session_feature_path()
    import csv
    with path.open(newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row["session_id"] == session_id:
                return score(row)
    return None


def score_from_event_id(event_id: str) -> dict[str, Any] | None:
    row = build_features_from_event_id(event_id)
    if row is None:
        return None
    return score(row)
