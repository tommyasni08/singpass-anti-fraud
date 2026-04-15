# ML-Based Score

This folder contains the machine-learning scoring layer for the Singpass Login Risk Engine.

The current baseline uses XGBoost on the login feature table, wrapped in an sklearn preprocessing pipeline for serving consistency.

## Purpose

The ML layer captures suspicious combinations of signals that are too broad or too brittle to encode purely as fixed rules.

## Contents

- `model_spec.md`: model design, split strategy, and feature scope
- `src/train_ml_baseline.py`: XGBoost training and evaluation script
- `generated/login_ml_scores.csv`: row-level ML predictions
- `generated/ml_evaluation_report.md`: evaluation summary
- `generated/feature_importance.csv`: feature importance export
- `generated/xgb_model.json`: saved model artifact
- `generated/serving_pipeline.joblib`: saved preprocessing-plus-model artifact for API inference
- `generated/serving_metadata.json`: expected feature groups and serving metadata

## Current status

Current XGBoost baseline on the holdout split at `ml_score >= 0.5`:

- review rate: `12.05%`
- recall: `88.70%`
- precision: `81.76%`

Current model takeaway:

- ML is the strongest standalone detector in the project
- the model is driven mainly by approval latency, session pressure, and recent user rejection history
- preprocessing is now packaged with the model so API inference uses the same transform path as training

## Input dependency

The ML layer consumes:

```text
singpass-login-risk-engine/feature_engineering/generated/login_features.csv
```

## How to run

From the repository root, using the project virtual environment:

```bash
python singpass-login-risk-engine/ml_based_score/src/train_ml_baseline.py
```

## Output location

Outputs are written to:

```text
singpass-login-risk-engine/ml_based_score/generated/
```
