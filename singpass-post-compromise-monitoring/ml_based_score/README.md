# ML-Based Score

This folder contains the machine-learning scoring layer for the Singpass Post-Compromise Monitoring project.

The current baseline is intended to model behavioural misuse at the session level without relying too heavily on direct rule-like downstream completion flags.

## Purpose

The ML layer is meant to capture softer post-login misuse patterns that the rule layer does not cover cleanly.

## Contents

- `model_spec.md`: model design, split strategy, and feature scope
- `src/train_ml_baseline.py`: session-level ML training and evaluation script

## Planned outputs

- `generated/post_login_ml_scores.csv`
- `generated/ml_evaluation_report.md`
- `generated/feature_importance.csv`
- `generated/xgb_model.json`

## Input dependency

The ML layer consumes:

```text
singpass-post-compromise-monitoring/feature_engineering/generated/post_login_session_features.csv
```

## How to run

From the repository root, using the project virtual environment:

```bash
./3.11_tasni_venv/bin/python singpass-post-compromise-monitoring/ml_based_score/src/train_ml_baseline.py
```
