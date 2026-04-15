from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

import joblib
import pandas as pd

from . import config
from .login_score_features import build_features_from_event_id


@lru_cache(maxsize=1)
def _login_metadata() -> dict[str, Any]:
    path = config.login_ml_dir() / "serving_metadata.json"
    return json.loads(path.read_text())


@lru_cache(maxsize=1)
def _login_model():
    return joblib.load(config.login_ml_dir() / "serving_pipeline.joblib")


def metadata() -> dict[str, Any]:
    meta = _login_metadata()
    return {
        "scoring_name": "login_score",
        "entity_key": "event_id",
        "numeric_features": meta["numeric_features"],
        "categorical_features": meta["categorical_features"],
        "notes": [
            "This endpoint accepts model-ready login features.",
            "Use the event-triggered login route to build features from the raw generated backend by event_id.",
            "The API returns rule, ML, and hybrid outputs together.",
            "Use the feature-engineering pipeline for offline training tables and the API for inference-time scoring.",
        ],
    }


def _to_float(value: Any) -> float | None:
    if value in {"", None}:
        return None
    return float(value)


def _to_int(value: Any) -> int:
    if value in {"", None}:
        return 0
    return int(float(value))


def _apply_rules(row: dict[str, Any]) -> list[str]:
    rules: list[str] = []
    latency = _to_float(row.get("approval_latency_seconds"))
    novelty_count = sum(
        _to_int(row.get(col, 0))
        for col in ["new_country_for_user_flag", "new_region_for_user_flag", "new_asn_for_user_flag"]
    )

    if row.get("login_event_type") == "qr_login_approved" and latency is not None and latency <= 2.0:
        rules.append("R01_fast_qr_approval")
    if _to_int(row.get("session_rejected_login_events_before_login")) >= 2:
        rules.append("R02_repeated_rejection_pressure")
    if _to_int(row.get("session_qr_request_count_before_login")) >= 4:
        rules.append("R03_high_attempt_volume_before_success")
    if (
        row.get("country") != "SG"
        and _to_int(row.get("new_country_for_user_flag")) == 1
        and latency is not None
        and latency <= 2.0
    ):
        rules.append("R04_foreign_and_new_country")
    if latency is not None and latency <= 2.0 and novelty_count >= 1:
        rules.append("R06_fast_approval_with_novelty")
    if _to_int(row.get("user_prior_rejected_login_count_7d")) >= 2:
        rules.append("R07_prior_rejection_history_plus_success")
    return rules


RULE_WEIGHTS = {
    "R01_fast_qr_approval": 2,
    "R02_repeated_rejection_pressure": 3,
    "R03_high_attempt_volume_before_success": 3,
    "R04_foreign_and_new_country": 2,
    "R06_fast_approval_with_novelty": 3,
    "R07_prior_rejection_history_plus_success": 2,
}


def _rule_band(score: int) -> str:
    if score >= 5:
        return "critical"
    if score >= 3:
        return "high"
    if score >= 1:
        return "medium"
    return "low"


def _is_strong_rule_case(triggered_rules: list[str]) -> bool:
    joined = "|".join(triggered_rules)
    return (
        "R02_repeated_rejection_pressure" in joined
        or "R03_high_attempt_volume_before_success" in joined
        or joined == "R06_fast_approval_with_novelty"
        or joined == "R01_fast_qr_approval"
    )


def _hybrid_policy(rule_band: str, triggered_rules: list[str], ml_score: float) -> tuple[str, str, int]:
    strong_rule_case = _is_strong_rule_case(triggered_rules)
    if strong_rule_case and ml_score >= 0.93:
        return "critical", "block_or_manual_review", 1
    if strong_rule_case:
        return "high", "step_up_or_manual_review", 1
    if ml_score >= 0.93:
        return "high", "step_up_or_manual_review", 1
    if 0.5 <= ml_score < 0.8 and rule_band == "medium":
        return "high", "step_up", 1
    if ml_score >= 0.50:
        return "medium", "allow_with_monitoring", 0
    if 0.3 <= ml_score < 0.5 and rule_band == "low":
        return "medium", "step_up", 1
    return "low", "allow", 0


def _prepare_model_frame(features: dict[str, Any]) -> pd.DataFrame:
    meta = _login_metadata()
    row = {}
    for col in meta["numeric_features"]:
        value = features.get(col, 0)
        row[col] = 0.0 if value in {"", None} else float(value)
    for col in meta["categorical_features"]:
        value = features.get(col, "unknown")
        row[col] = "unknown" if value in {"", None} else str(value)
    ordered = {col: row[col] for col in meta["numeric_features"] + meta["categorical_features"]}
    return pd.DataFrame([ordered])


def _explanations(triggered_rules: list[str], ml_score: float, hybrid_action: str) -> list[str]:
    out = []
    if triggered_rules:
        out.append(f"Triggered rules: {', '.join(triggered_rules)}")
    if ml_score >= 0.93:
        out.append("ML score is in the highest-risk review band.")
    elif ml_score >= 0.5:
        out.append("ML score is elevated.")
    elif ml_score >= 0.3:
        out.append("ML score is in the lower intervention range.")
    out.append(f"Hybrid action selected: {hybrid_action}")
    return out


def score(features: dict[str, Any]) -> dict[str, Any]:
    event_id = str(features.get("event_id") or "login_score_request")
    triggered_rules = _apply_rules(features)
    rule_score = sum(RULE_WEIGHTS[name] for name in triggered_rules)
    rule_risk_band = _rule_band(rule_score)

    model_df = _prepare_model_frame(features)
    ml_score = float(_login_model().predict_proba(model_df)[0][1])
    hybrid_risk_band, hybrid_action, hybrid_review_flag = _hybrid_policy(rule_risk_band, triggered_rules, ml_score)

    return {
        "scoring_name": "login_score",
        "entity_id": event_id,
        "rule_score": rule_score,
        "rule_risk_band": rule_risk_band,
        "triggered_rules": triggered_rules,
        "ml_score": ml_score,
        "hybrid_risk_band": hybrid_risk_band,
        "hybrid_action": hybrid_action,
        "hybrid_review_flag": hybrid_review_flag,
        "explanations": _explanations(triggered_rules, ml_score, hybrid_action),
    }


def score_from_event_id(event_id: str) -> dict[str, Any] | None:
    row = build_features_from_event_id(event_id)
    if row is None:
        return None
    return score(row)
