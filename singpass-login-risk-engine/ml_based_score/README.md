# ML-Based Score

This folder contains the machine-learning baseline for the Singpass Login Risk Engine.

## Contents

- `model_spec.md`: baseline ML design and modeling assumptions
- `src/train_ml_baseline.py`: trains and evaluates the first ML scoring model
- `generated/`: prediction outputs and evaluation report

## Input dependency

The ML layer consumes:

```text
singpass-login-risk-engine/feature_engineering/generated/login_features.csv
```

## How to run

From the repository root:

```bash
python singpass-login-risk-engine/ml_based_score/src/train_ml_baseline.py
```

Preferred runtime:

- activate the project virtual environment first
- or invoke the script with the virtual-environment interpreter directly

## Current outputs

- `login_ml_scores.csv`
- `ml_evaluation_report.md`
- `feature_importance.csv`
- `xgb_model.json`

Both outputs are written to:

```text
singpass-login-risk-engine/ml_based_score/generated/
```
