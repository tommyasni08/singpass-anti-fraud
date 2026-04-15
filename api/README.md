# API

This folder contains the scoring API for the Singpass anti-fraud portfolio.

The API serves two scoring surfaces:

- `login_score`
- `session_score`

These names are intentionally user-facing and operationally clear:

- `login_score` maps to the live login prevention system
- `session_score` maps to the post-login monitoring and containment system

## Design choice

Version 1 uses feature-level scoring inputs.

Why:

- the current repository already has strong offline feature pipelines
- production systems usually score on model-ready features or their online equivalent
- this keeps the service honest to the current architecture instead of duplicating raw-event feature engineering inside the API

For demo purposes, the API also supports scoring directly from existing generated feature-table record IDs:

- `POST /login_score/from_event`
- `GET /login_score/from_event/{event_id}`
- `POST /session_score/from_event`
- `GET /session_score/from_session/{session_id}`

Both scoring surfaces now load serving-safe sklearn pipeline artifacts:

- `login_score` loads the saved project-1 preprocessing pipeline and XGBoost model bundle
- `session_score` loads the saved project-2 preprocessing pipeline and XGBoost model bundle

This keeps training-time preprocessing and API inference consistent.

## Endpoints

- `GET /health`
- `GET /metadata/login_score`
- `GET /metadata/session_score`
- `POST /login_score`
- `POST /login_score/from_event`
- `GET /login_score/from_event/{event_id}`
- `POST /session_score`
- `POST /session_score/from_event`
- `GET /session_score/from_session/{session_id}`

The event-triggered login route is the more production-like path for project 1:

- it accepts a successful login event identifier
- it builds login features from the raw generated backend tables
- it then applies rule, ML, and hybrid scoring

The original `POST /login_score` endpoint remains useful for:

- debugging
- scorer validation
- direct feature-level testing

The event-triggered session route is the more production-like path for project 2:

- it accepts a post-login event identifier
- it resolves the session behind that event
- it rebuilds the monitored session feature row from the raw generated backend tables
- it then applies rule, ML, and hybrid scoring

## How to run

From the repository root:

```bash
../3.11_tasni_venv/bin/uvicorn api.app.main:app --reload
```

## Example request

```bash
curl -X POST http://127.0.0.1:8000/login_score \
  -H "Content-Type: application/json" \
  -d '{
    "features": {
      "approval_latency_seconds": 1.5,
      "approval_latency_missing_flag": 0,
      "login_hour_of_day": 2,
      "service_supports_myinfo_flag": 1,
      "service_supports_signing_flag": 1,
      "user_device_link_exists_flag": 1,
      "is_primary_device_flag": 1,
      "new_country_for_user_flag": 1,
      "new_region_for_user_flag": 1,
      "new_asn_for_user_flag": 1,
      "session_event_count_before_login": 5,
      "session_failed_login_events_before_login": 0,
      "session_rejected_login_events_before_login": 2,
      "session_qr_request_count_before_login": 4,
      "session_qr_prompt_count_before_login": 3,
      "session_has_lifecycle_event_before_login_flag": 0,
      "session_lifecycle_event_count_before_login": 0,
      "session_has_contact_detail_updated_before_login_flag": 0,
      "user_prior_login_count_7d": 1,
      "user_prior_successful_login_count_7d": 0,
      "user_prior_rejected_login_count_7d": 2,
      "user_prior_distinct_services_30d": 1,
      "user_prior_distinct_countries_30d": 1,
      "user_prior_distinct_asns_30d": 1,
      "days_since_last_successful_login": 0,
      "days_since_last_successful_login_missing_flag": 1,
      "device_prior_login_count_30d": 1,
      "device_prior_distinct_users_30d": 1,
      "device_used_by_multiple_users_flag": 0,
      "first_time_service_for_user_flag": 1,
      "service_used_by_user_last_30d_flag": 0,
      "service_usage_count_by_user_30d": 0,
      "login_event_type": "qr_login_approved",
      "login_method": "qr_login",
      "channel": "mobile_app",
      "service_sector_type": "banking",
      "service_risk_tier": "high",
      "trust_status": "trusted",
      "country": "MY",
      "region": "MY_WEST",
      "event_id": "demo_login_event"
    }
  }'
```

Example event-triggered request:

```bash
curl -X POST http://127.0.0.1:8000/login_score/from_event \
  -H "Content-Type: application/json" \
  -d '{
    "event_id": "E00000002"
  }'
```

Example session-triggered request:

```bash
curl -X POST http://127.0.0.1:8000/session_score/from_event \
  -H "Content-Type: application/json" \
  -d '{
    "event_id": "E00000010"
  }'
```

## Current limitation

This API is a scoring layer, not a full online feature-computation platform.

That means:

- the offline pipelines remain the source of training features
- the login scorer now includes a synchronous feature-on-read path for successful login triggers
- the session scorer now includes the same feature-on-read pattern for post-login event triggers
- a later scope can extend this into a fuller online feature transformation layer with shared state or streaming infrastructure

This is the correct MVP serving shape for the current repository.
