# Feature Engineering

This folder contains the feature-engineering work for the Singpass Login Risk Engine.

## Contents

- `feature_spec.md`: feature design and modeling assumptions
- `src/generate_login_features.py`: version 1 feature-table generator
- `generated/`: exported feature outputs and quality checks

## How to run

From the repository root:

```bash
python3 singpass-login-risk-engine/feature_engineering/src/generate_login_features.py
```

## Current outputs

The first version generates:

- `login_features.csv`
- `feature_quality_report.md`

Both outputs are written to:

```text
singpass-login-risk-engine/feature_engineering/generated/
```
