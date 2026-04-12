# Hybrid Score

This folder contains the policy-based hybrid scoring layer for the Singpass Login Risk Engine.

## Contents

- `hybrid_spec.md`: hybrid decision policy design
- `src/generate_hybrid_scores.py`: joins rule and ML outputs and applies the decision policy
- `generated/`: hybrid scores and evaluation report

## Input dependencies

The hybrid layer consumes:

```text
singpass-login-risk-engine/rule_based_score/generated/login_rule_scores.csv
singpass-login-risk-engine/ml_based_score/generated/login_ml_scores.csv
```

## How to run

From the repository root:

```bash
python3 singpass-login-risk-engine/hybrid_score/src/generate_hybrid_scores.py
```

## Current outputs

- `hybrid_scores.csv`
- `hybrid_evaluation_report.md`

Both outputs are written to:

```text
singpass-login-risk-engine/hybrid_score/generated/
```
