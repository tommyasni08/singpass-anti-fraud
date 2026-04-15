from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class FeaturePayload(BaseModel):
    features: dict[str, Any] = Field(default_factory=dict)


class EventTriggerPayload(BaseModel):
    event_id: str


class ScoreResponse(BaseModel):
    scoring_name: str
    entity_id: str
    rule_score: int
    rule_risk_band: str
    triggered_rules: list[str]
    ml_score: float
    hybrid_risk_band: str
    hybrid_action: str
    hybrid_review_flag: int
    explanations: list[str]


class MetadataResponse(BaseModel):
    scoring_name: str
    entity_key: str
    numeric_features: list[str]
    categorical_features: list[str]
    notes: list[str]


class HealthResponse(BaseModel):
    status: str
