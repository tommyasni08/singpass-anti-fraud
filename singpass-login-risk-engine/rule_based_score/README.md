# Rule-Based Score

This folder contains the interpretable rule layer for the Singpass Login Risk Engine.

## Contents

- `rules_spec.md`: baseline rule design
- `src/generate_rule_scores.py`: rule-scoring generator
- `generated/`: rule outputs and rule-quality review

## Input dependency

The rule layer consumes:

```text
singpass-login-risk-engine/feature_engineering/generated/login_features.csv
```

## How to run

From the repository root:

```bash
python3 singpass-login-risk-engine/rule_based_score/src/generate_rule_scores.py
```

## Current outputs

- `login_rule_scores.csv`
- `rule_quality_report.md`

Both outputs are written to:

```text
singpass-login-risk-engine/rule_based_score/generated/
```
