# MLOps Architecture

Last updated: 15 April 2026

## Purpose

This document describes how the Singpass anti-fraud portfolio can be moved from a local portfolio implementation into a production-style MLOps architecture on Google Cloud.

The goal is not to claim that the current repository is already deployed. The goal is to show:

- how the current layers map into deployable services
- how model training, serving, and monitoring would be separated
- how both `login_score` and `session_score` fit into one operational platform

## Current local layers

The repository already has the right conceptual boundaries:

- `data/`
  - shared synthetic backend generation
- `pipelines/`
  - offline orchestration
- `singpass-login-risk-engine/`
  - project-1 feature, rule, ML, and hybrid scoring stack
- `singpass-post-compromise-monitoring/`
  - project-2 feature, rule, ML, and hybrid scoring stack
- `api/`
  - online scoring interface
- `monitoring/`
  - dashboard-ready operational summaries

This means the portfolio already resembles a minimum viable ML platform:

- offline data and training side
- online inference side
- reporting and monitoring side

## Google Cloud target architecture

The recommended target environment on Google Cloud is:

1. **Storage and analytical layer**
- Cloud Storage
- BigQuery

2. **Event and online ingestion layer**
- Pub/Sub
- Cloud Run

3. **Feature and batch transformation layer**
- Dataflow or scheduled Cloud Run Jobs
- BigQuery feature tables

4. **Model training and registry layer**
- Vertex AI Training
- Vertex AI Model Registry
- Artifact Registry

5. **Online serving layer**
- Cloud Run for API services
- Vertex AI endpoints only if model-only serving becomes preferable later

6. **Monitoring and dashboard layer**
- BigQuery monitoring tables
- Looker Studio or Streamlit on Cloud Run
- Cloud Monitoring and Cloud Logging

## Recommended service mapping

### 1. Raw event storage

**Current repo equivalent**
- `data/input_data/generated/events.csv`
- `data/input_data/generated/sessions.csv`
- `data/input_data/generated/fraud_labels.csv`

**Google Cloud target**
- raw event drops in Cloud Storage
- canonical event and session tables in BigQuery

Why:
- Cloud Storage is the landing zone
- BigQuery becomes the analytical system of record for feature jobs, monitoring, and retrospective evaluation

### 2. Event-triggered scoring

**Current repo equivalent**
- `api/`
- `POST /login_score/from_event`
- `POST /session_score/from_event`

**Google Cloud target**
- Pub/Sub for event triggers
- Cloud Run scoring service subscribed to scoring-trigger events

Recommended trigger pattern:
- successful login events trigger `login_score`
- post-login activity events trigger `session_score`

Why:
- Pub/Sub decouples producers from scoring services
- Cloud Run fits HTTP and event-driven inference well

### 3. Online feature transformation

**Current repo equivalent**
- `api/app/login_score_features.py`
- `api/app/session_score_features.py`

**Google Cloud target**
- synchronous feature-on-read logic inside Cloud Run for version 1
- later move reusable feature logic into shared feature services or BigQuery materialized views if needed

Why:
- this matches the current repo design
- it is the lowest-friction move from local code to deployable service
- it avoids pretending a feature store already exists

### 4. Offline feature pipelines

**Current repo equivalent**
- project feature engineering scripts
- `pipelines/src/run_pipeline.py`

**Google Cloud target**
- scheduled Cloud Run Jobs for smaller workloads
- Dataflow for larger event-volume transforms later
- BigQuery output tables for:
  - login features
  - post-login session features

Why:
- feature generation is batch-oriented
- retraining and monitoring should read stable feature tables, not raw event logs directly

### 5. Model training

**Current repo equivalent**
- ML training scripts under both projects
- local generated model artifacts

**Google Cloud target**
- Vertex AI custom training jobs
- training inputs from BigQuery extracts or Cloud Storage exports
- model artifacts written to Cloud Storage and registered in Vertex AI Model Registry

Why:
- clean separation of training from serving
- model versioning becomes explicit
- easier audit trail for thresholds and model revisions

### 6. Artifact packaging

**Current repo equivalent**
- `serving_pipeline.joblib`
- `serving_metadata.json`

**Google Cloud target**
- model bundles stored in Cloud Storage
- container images in Artifact Registry
- model metadata registered in Vertex AI Model Registry

Why:
- inference services should pull stable versioned artifacts
- deployment should not depend on local generated folders

### 7. Online inference services

**Current repo equivalent**
- FastAPI app under `api/`

**Google Cloud target**
- Cloud Run service for the scoring API

Recommended route split:
- `/login_score`
- `/login_score/from_event`
- `/session_score`
- `/session_score/from_event`

Why Cloud Run:
- good fit for Python API workloads
- easy deployment from container image
- scales without managing servers

### 8. Monitoring and dashboarding

**Current repo equivalent**
- `monitoring/`
- Streamlit dashboard

**Google Cloud target**
- monitoring summary tables in BigQuery
- Streamlit dashboard on Cloud Run or Looker Studio over BigQuery
- Cloud Logging for request and inference logs
- Cloud Monitoring alerts for service health

Why:
- operational summaries should persist independently of the model code
- dashboard consumers should read monitoring tables, not directly invoke training or scoring logic

## Proposed end-to-end Google Cloud flow

### A. Online scoring path

1. application emits event
2. event lands in Pub/Sub
3. scoring-trigger event invokes Cloud Run API
4. API fetches required context from BigQuery or a serving-side cache
5. feature builder creates model-ready input
6. rule layer, ML layer, and hybrid policy score the event or session
7. result is written to:
   - operational action table in BigQuery
   - Cloud Logging
   - optional downstream review queue

### B. Offline retraining path

1. scheduled batch job refreshes raw and curated tables
2. feature pipeline builds training feature tables
3. Vertex AI training job trains latest models
4. evaluation metrics are written to monitoring tables
5. approved model version is registered
6. serving service is redeployed or switched to the new model artifact

### C. Monitoring path

1. scored outputs land in BigQuery
2. monitoring job aggregates:
   - review rate
   - action distribution
   - recall / precision on labelled backfills
   - score-band distribution
   - feature null-rate drift
3. dashboard reads those summaries
4. alerts are triggered for:
   - scoring failure spikes
   - queue growth
   - drift or performance degradation

## Recommended Google Cloud components by layer

| Layer | Recommended Google Cloud Service |
| --- | --- |
| Raw file landing | Cloud Storage |
| Structured analytical tables | BigQuery |
| Event bus | Pub/Sub |
| Scoring API | Cloud Run |
| Batch orchestration | Cloud Run Jobs |
| Heavier streaming/batch transform later | Dataflow |
| Model training | Vertex AI Training |
| Model registry | Vertex AI Model Registry |
| Container registry | Artifact Registry |
| Logs and service metrics | Cloud Logging, Cloud Monitoring |
| Dashboard | Streamlit on Cloud Run or Looker Studio |

## Recommended deployment shape for this portfolio

The best pragmatic deployment order is:

### Phase 1
- containerize the FastAPI app
- deploy `api/` to Cloud Run
- store current serving artifacts in Cloud Storage
- keep BigQuery as the source for context lookup and monitoring tables

### Phase 2
- move local pipeline entrypoints into Cloud Run Jobs
- write feature tables and monitoring outputs into BigQuery
- schedule retraining and monitoring refresh jobs

### Phase 3
- move model training to Vertex AI
- introduce model version promotion flow
- add alerting and dashboard drilldowns

This sequence matches the current maturity of the repository and avoids overengineering too early.

## Minimum production table groups

If moved to BigQuery, the main table groups should be:

### Raw domain tables
- `raw_events`
- `raw_sessions`
- `raw_users`
- `raw_devices`
- `raw_services`

### Curated feature tables
- `login_features_daily`
- `post_login_session_features_daily`

### Scoring output tables
- `login_score_results`
- `session_score_results`

### Monitoring tables
- `ops_review_queue_summary`
- `ops_action_distribution_daily`
- `metrics_model_performance_daily`
- `metrics_feature_quality_daily`

This supports the monitoring split you described later:

- `ops view`
- `metrics view`

## How the current repo maps to that future state

### Current local
- CSV files
- local scripts
- local API
- local monitoring artifacts

### Future Google Cloud
- BigQuery tables
- Cloud Run Jobs
- Cloud Run scoring API
- Vertex AI training jobs
- dashboard backed by BigQuery monitoring tables

So the portfolio is already architecturally compatible with that migration.

## Key design decisions

### 1. Keep rule and ML outputs both available

Why:
- rules provide explicit intervention logic
- ML provides broader pattern detection
- hybrid policy remains the operational layer

### 2. Keep scoring and monitoring separated

Why:
- online scoring should stay fast and narrow
- monitoring should aggregate and explain system behavior asynchronously

### 3. Keep event-triggered scoring

Why:
- this matches the real fraud-control workflow better than scoring static feature payloads only
- login and post-login events naturally trigger evaluation

### 4. Use BigQuery as the shared analytical backbone

Why:
- both projects depend on shared context
- monitoring and retraining both benefit from one analytical source

## What is intentionally not claimed

This portfolio does not currently implement:

- real Google Cloud deployment
- streaming state stores
- model registry promotion workflows
- online feature store
- automated canary rollout

Those are next-step design targets, not current implemented capabilities.

## Recruiter-facing interpretation

This architecture shows that the portfolio already thinks in the right production shape:

- batch data pipelines
- online inference
- artifact packaging
- monitoring and dashboarding
- cloud deployment boundary
- separation between prevention and containment systems

That is the main reason to include this document.
