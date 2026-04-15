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

Version 1 focuses on static monitoring artifacts generated from the latest portfolio outputs:

- login-score operational summary
- session-score operational summary
- action distribution
- review rate
- recall and precision at the selected operating point
- simple score-band distribution
- basic feature-table data quality checks

This is the correct first step before adding a live dashboard.

## Entrypoint

From the repository root:

```bash
python monitoring/src/generate_monitoring_reports.py
```

Or using the project virtual environment explicitly:

```bash
../3.11_tasni_venv/bin/python monitoring/src/generate_monitoring_reports.py
```

## Outputs

Generated outputs are written to:

```text
monitoring/generated/
```

Current artifacts:

- `portfolio_monitoring_report.md`
- `portfolio_monitoring_summary.json`
- `login_score_monitoring.csv`
- `session_score_monitoring.csv`
- `last_monitoring_manifest.json`

## Intended future extension

This layer is designed so a later scope can add:

- daily batch monitoring jobs
- score drift tracking over time
- feature null-rate drift
- review queue trend charts
- a Streamlit or web dashboard
