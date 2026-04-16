# Monitoring Dashboard

This folder contains a Streamlit dashboard for the Singpass anti-fraud portfolio.

The dashboard reads from:

- `monitoring/generated/portfolio_monitoring_report.md`
- `monitoring/generated/portfolio_monitoring_summary.json`
- `monitoring/generated/login_score_ops.csv`
- `monitoring/generated/login_score_metrics.csv`
- `monitoring/generated/login_score_review_cases.csv`
- `monitoring/generated/session_score_ops.csv`
- `monitoring/generated/session_score_metrics.csv`
- `monitoring/generated/session_score_review_cases.csv`
- `monitoring/generated/last_monitoring_manifest.json`

It does not retrain models or recompute scores. It visualizes the latest generated monitoring outputs.

## How to run

From the repository root:

```bash
./singpass_anti_fraud_venv/bin/streamlit run monitoring/dashboard/app.py
```

Before running the dashboard, make sure the monitoring outputs are refreshed:

```bash
./singpass_anti_fraud_venv/bin/python monitoring/src/generate_monitoring_reports.py
```

## Current views

- ops view
- metrics view
- latest monitoring report and manifest
