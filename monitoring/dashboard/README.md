# Monitoring Dashboard

This folder contains a Streamlit dashboard for the Singpass anti-fraud portfolio.

The dashboard reads from:

- `monitoring/generated/portfolio_monitoring_report.md`
- `monitoring/generated/portfolio_monitoring_summary.json`
- `monitoring/generated/login_score_monitoring.csv`
- `monitoring/generated/session_score_monitoring.csv`
- `monitoring/generated/last_monitoring_manifest.json`

It does not retrain models or recompute scores. It visualizes the latest generated monitoring outputs.

## How to run

From the repository root:

```bash
../3.11_tasni_venv/bin/streamlit run monitoring/dashboard/app.py
```

Before running the dashboard, make sure the monitoring outputs are refreshed:

```bash
../3.11_tasni_venv/bin/python monitoring/src/generate_monitoring_reports.py
```

## Current views

- portfolio summary
- login-score operational metrics
- session-score operational metrics
- action distribution
- ML score-band distribution
- latest monitoring report and manifest
