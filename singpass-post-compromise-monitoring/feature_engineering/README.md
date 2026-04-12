# Feature Engineering

This folder builds the session-level monitoring table for the Singpass Post-Compromise Monitoring project.

It converts the shared synthetic backend into one scored row per monitored post-login session.

## Purpose

This layer defines the model-ready input for the downstream project-2 scoring stack:

- rule-based post-login monitoring
- ML-based post-login monitoring
- later hybrid containment policy

The current analytical unit is:

- one row per authenticated session with at least one modeled post-login event

## Contents

- `feature_spec.md`: session-level feature definitions, joins, and null-handling rules
- `src/generate_post_login_session_features.py`: feature-table generator
- `generated/post_login_session_features.csv`: session-level monitoring table
- `generated/feature_quality_report.md`: feature inspection and quality checks

## Current status

Current output size:

- `38,834` monitored sessions
- `6,757` fraud-labelled sessions
- `32,077` non-fraud sessions

Current feature observations:

- the table is strong for rule design because explicit downstream misuse is visible at the session level
- the table is also usable for ML, but only after removing direct label-proxy features from the behavioural baseline
- nulls are concentrated in the expected places:
  - no sensitive event in session
  - no service switch in session
  - no prior session history yet

## How to run

From the repository root:

```bash
python3 singpass-post-compromise-monitoring/feature_engineering/src/generate_post_login_session_features.py
```

## Output location

Outputs are written to:

```text
singpass-post-compromise-monitoring/feature_engineering/generated/
```
