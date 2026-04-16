# Monitoring

This folder contains operational monitoring outputs for the Singpass anti-fraud portfolio.

The monitoring layer sits after:

- `pipelines/`
- model training
- rule scoring
- hybrid scoring
- `api/`

Its purpose is to turn scored outputs into dashboard-ready summaries.

## Current scope

Version 1 now splits monitoring into two views generated from the latest portfolio outputs:

- `ops view`
  - review volume
  - action distribution
  - reviewed-scenario mix
  - top reviewed login and session cases
- `metrics view`
  - recall
  - precision
  - ML score-band distribution
  - data-quality missingness indicators

This is the correct first production-style monitoring split for the repository.

## Entrypoint

From the repository root:

```bash
python monitoring/src/generate_monitoring_reports.py
```

Or using the project virtual environment explicitly:

```bash
./singpass_anti_fraud_venv/bin/python monitoring/src/generate_monitoring_reports.py
```

## Outputs

Generated outputs are written to:

```text
monitoring/generated/
```

Current artifacts:

- `portfolio_monitoring_report.md`
- `portfolio_monitoring_summary.json`
- `login_score_ops.csv`
- `login_score_metrics.csv`
- `login_score_review_cases.csv`
- `session_score_ops.csv`
- `session_score_metrics.csv`
- `session_score_review_cases.csv`
- `last_monitoring_manifest.json`

## Intended future extension

This layer is designed so a later scope can add:

- daily batch monitoring jobs
- score drift tracking over time
- feature null-rate drift
- review queue trend charts
- deeper review-queue drilldowns
- time-series ops and metrics trends
