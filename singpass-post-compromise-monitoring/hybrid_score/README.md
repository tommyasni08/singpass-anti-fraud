# Hybrid Score

This folder contains the final policy-based hybrid decision layer for the Singpass Post-Compromise Monitoring project.

It combines explicit downstream containment rules with behavioural ML scoring.

## Current contents

- `generated/model_comparison.md`: rule-only vs ML-only comparison
- `hybrid_spec.md`
- `src/generate_hybrid_scores.py`
- `generated/post_login_hybrid_scores.csv`
- `generated/hybrid_evaluation_report.md`

## Current status

Current final hybrid policy: `v1`

Operating priority:

- maximize containment recall

Current hybrid v1 result:

- review rate: `18.08%`
- recall: `99.48%`
- precision: `95.73%`
