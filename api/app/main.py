from __future__ import annotations

from fastapi import FastAPI, HTTPException

from .login_score import metadata as login_metadata
from .login_score import score as score_login
from .login_score import score_from_event_id
from .schemas import EventTriggerPayload, FeaturePayload, HealthResponse, MetadataResponse, ScoreResponse
from .session_score import metadata as session_metadata
from .session_score import score as score_session
from .session_score import score_from_event_id as score_session_from_event_id
from .session_score import score_from_session_id


app = FastAPI(
    title="Singpass Anti-Fraud Scoring API",
    version="0.1.0",
    description="Serving layer for login_score and session_score.",
)


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(status="ok")


@app.get("/metadata/login_score", response_model=MetadataResponse)
def login_score_metadata() -> MetadataResponse:
    return MetadataResponse(**login_metadata())


@app.get("/metadata/session_score", response_model=MetadataResponse)
def session_score_metadata() -> MetadataResponse:
    return MetadataResponse(**session_metadata())


@app.post("/login_score", response_model=ScoreResponse)
def login_score(payload: FeaturePayload) -> ScoreResponse:
    return ScoreResponse(**score_login(payload.features))


@app.post("/login_score/from_event", response_model=ScoreResponse)
def login_score_from_event_payload(payload: EventTriggerPayload) -> ScoreResponse:
    result = score_from_event_id(payload.event_id)
    if result is None:
        raise HTTPException(status_code=404, detail="event_id not found in raw login event source or not scoreable")
    return ScoreResponse(**result)


@app.get("/login_score/from_event/{event_id}", response_model=ScoreResponse)
def login_score_from_event(event_id: str) -> ScoreResponse:
    result = score_from_event_id(event_id)
    if result is None:
        raise HTTPException(status_code=404, detail="event_id not found in raw login event source or not scoreable")
    return ScoreResponse(**result)


@app.post("/session_score", response_model=ScoreResponse)
def session_score_endpoint(payload: FeaturePayload) -> ScoreResponse:
    return ScoreResponse(**score_session(payload.features))


@app.post("/session_score/from_event", response_model=ScoreResponse)
def session_score_from_event_payload(payload: EventTriggerPayload) -> ScoreResponse:
    result = score_session_from_event_id(payload.event_id)
    if result is None:
        raise HTTPException(status_code=404, detail="event_id not found in raw post-login event source or not scoreable")
    return ScoreResponse(**result)


@app.get("/session_score/from_session/{session_id}", response_model=ScoreResponse)
def session_score_from_session(session_id: str) -> ScoreResponse:
    result = score_from_session_id(session_id)
    if result is None:
        raise HTTPException(status_code=404, detail="session_id not found in session feature table")
    return ScoreResponse(**result)
