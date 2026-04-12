# Hybrid Score

This folder will contain the final policy-based hybrid decision layer for the Singpass Post-Compromise Monitoring project.

The current comparison artifact is already placed here because the hybrid design should be based on the observed tradeoff between:

- explicit downstream rules
- behavioural ML scoring

## Current contents

- `generated/model_comparison.md`: rule-only vs ML-only comparison

## Planned next contents

- `hybrid_spec.md`
- `src/generate_hybrid_scores.py`
- `generated/post_login_hybrid_scores.csv`
- `generated/hybrid_evaluation_report.md`
