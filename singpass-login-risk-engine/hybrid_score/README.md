# Hybrid Score

This folder contains the policy-based hybrid decision layer for the Singpass Login Risk Engine.

It combines explicit rule evidence with ML risk scores to produce operational actions.

## Purpose

The hybrid layer is the final decisioning output of project 1.

It is designed to:

- preserve rule-based explainability
- use ML for broader fraud capture
- tune decisions against operational constraints such as review rate, recall, and precision

## Contents

- `hybrid_spec.md`: final hybrid policy design
- `src/generate_hybrid_scores.py`: hybrid scorer
- `generated/hybrid_scores.csv`: row-level hybrid outputs
- `generated/hybrid_evaluation_report.md`: final hybrid results
- `generated/tuning_analysis.md`: tuning process and selected operating point
- `generated/model_comparison.md`: rule-only vs ML-only vs hybrid comparison

## Current status

Current final hybrid policy: `v3`

Operating target:

- review rate under `12%`
- maximize recall
- precision above `85%`

Final hybrid v3 result:

- review rate: `10.46%`
- recall: `80.96%`
- precision: `85.93%`

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

## Output location

Outputs are written to:

```text
singpass-login-risk-engine/hybrid_score/generated/
```
