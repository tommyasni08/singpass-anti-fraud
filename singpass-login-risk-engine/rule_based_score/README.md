# Rule-Based Score

This folder contains the interpretable rule layer for the Singpass Login Risk Engine.

It is designed to catch explicit high-confidence login-risk patterns before ML is applied.

## Purpose

The rule layer provides:

- transparent fraud logic
- reviewer-friendly explanations
- a baseline decisioning layer for comparison with ML

## Contents

- `rules_spec.md`: tuned rule definitions and scoring logic
- `src/generate_rule_scores.py`: rule-scoring generator
- `generated/login_rule_scores.csv`: row-level rule outputs
- `generated/rule_quality_report.md`: rule evaluation and per-rule quality review

## Current status

Current tuned rule baseline:

- review threshold: `rule_score >= 3`
- review rate: `10.81%`
- recall: `78.05%`
- precision: `80.14%`

Strongest current rules:

- repeated rejection pressure
- high attempt volume before success
- fast approval with novelty

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

## Output location

Outputs are written to:

```text
singpass-login-risk-engine/rule_based_score/generated/
```
