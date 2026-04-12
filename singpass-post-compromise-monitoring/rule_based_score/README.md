# Rule-Based Score

This folder contains the interpretable post-login monitoring rule layer for the Singpass Post-Compromise Monitoring project.

It is designed to catch explicit downstream misuse patterns after access has already been obtained.

## Purpose

The rule layer provides:

- transparent post-login misuse logic
- reviewer-friendly explanations
- a baseline containment layer before ML is added

## Contents

- `src/generate_rule_scores.py`: rule-scoring generator
- `generated/post_login_rule_scores.csv`: row-level rule outputs
- `generated/rule_quality_report.md`: rule evaluation and per-rule review
- `rules_spec.md`: first post-login rule definitions and scoring logic

## Current status

Current tuned rule baseline:

- review threshold: `rule_score >= 3`
- review rate: `12.89%`
- recall: `74.07%`
- precision: `100.00%`

Interpretation:

- the rule layer is deliberately strict and explicit
- it acts as a clean containment baseline rather than a broad detector

## Input dependency

The rule layer will consume:

```text
singpass-post-compromise-monitoring/feature_engineering/generated/post_login_session_features.csv
```
