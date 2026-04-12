# Hybrid Tuning Analysis

Last updated: 12 April 2026

## Operating goal

- keep review rate under `12%`
- maximize recall
- keep precision above `85%`

## Key finding

The coarse hybrid v1 policy could not meet the target.

The main issue was:

- the `critical` rule band was too mixed internally
- some critical rule combinations were close to deterministic fraud
- others were only around `64%` precision

So rule band alone was too coarse for the tuning goal.

## Grid analysis highlights

Selected high-value cells from the `rule_band x ml_score_bucket` grid:

- `low x >=0.93`: very high fraud concentration
- `medium x >=0.93`: very high fraud concentration
- `high x >=0.93`: very high fraud concentration
- `critical x >=0.93`: still useful, but not as clean as the best rule-combination buckets

## Strong-rule findings

The following rule situations were strong enough to preserve in the hybrid policy:

- any case containing `R02_repeated_rejection_pressure`
- any case containing `R03_high_attempt_volume_before_success`
- exact `R06_fast_approval_with_novelty`
- exact `R01_fast_qr_approval`

These were chosen because they had very high precision in the current data.

## Candidate policies tested

### Coarse hybrid v1

- review rate: `12.04%`
- recall: `88.64%`
- precision: `81.76%`

Result:

- misses the precision target

### ML-only threshold sweep

- `0.92`: review rate `11.42%`, recall `86.09%`, precision `83.72%`
- `0.93`: review rate around `10%`, better precision, but still benefits from rule support
- `0.94`: review rate `7.73%`, recall `65.22%`, precision `93.66%`

Result:

- higher threshold improves precision, but recall drops quickly

### Tuned hybrid v2

Policy:

- review if `ml_score >= 0.93`
- or if the case matches a strong-rule condition

Result:

- review rate: `10.21%`
- recall: `79.82%`
- precision: `86.86%`

### Tuned hybrid v3

Policy adjustments:

- keep the `ml_score >= 0.93` review threshold
- keep the selected strong-rule conditions
- additionally escalate two small high-value pockets:
  - `rule_risk_band = low` and `0.30 <= ml_score < 0.50`
  - `rule_risk_band = medium` and `0.50 <= ml_score < 0.80`

Result:

- review rate: `10.46%`
- recall: `80.96%`
- precision: `85.93%`

## Decision

Hybrid v3 was selected because it is the best current policy that satisfies the stated operating goal.
