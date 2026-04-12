# Feature Engineering

This folder builds the login-stage feature table for the Singpass Login Risk Engine.

It converts the shared synthetic backend into one scored row per successful decisive login outcome.

## Purpose

This layer defines the model-ready input for both downstream scoring approaches:

- rule-based score
- ML-based score

The current scored population is limited to:

- `app_login_success`
- `qr_login_approved`

## Contents

- `feature_spec.md`: feature definitions, joins, and null-handling rules
- `src/generate_login_features.py`: feature-table generator
- `generated/login_features.csv`: scored login feature table
- `generated/feature_quality_report.md`: feature inspection and quality checks

## Current status

Current output size:

- `39,538` scored login rows
- `4,391` fraud-labelled rows
- `35,147` non-fraud rows

Current feature observations:

- `approval_latency_seconds` is the strongest single signal
- rejection-pressure and session-attempt features are useful login-risk context
- `days_since_last_successful_login` is intentionally nullable for first-observed successful logins

## How to run

From the repository root:

```bash
python3 singpass-login-risk-engine/feature_engineering/src/generate_login_features.py
```

## Output location

Outputs are written to:

```text
singpass-login-risk-engine/feature_engineering/generated/
```
