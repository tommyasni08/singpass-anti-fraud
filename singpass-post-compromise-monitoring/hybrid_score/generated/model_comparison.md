# Model Comparison

Last updated: 12 April 2026

## Purpose

This document compares the two current post-login monitoring approaches on the same session population:

- rule-only
- ML-only

The goal is to justify how the hybrid containment policy should be designed next.

## Comparison basis

Both approaches are evaluated on the same `38,834` monitored post-login sessions.

Total fraud sessions:

- `6,757`

Operational definitions used for comparison:

- rule-only: `rule_review_flag = 1` which corresponds to `rule_score >= 3`
- ML-only: `ml_score >= 0.5`

## Summary table

| Approach | Review Rows | Review Rate | Fraud Caught | Recall | Precision |
| --- | ---: | ---: | ---: | ---: | ---: |
| Rule-only | 5,005 | 12.89% | 5,005 | 74.07% | 100.00% |
| ML-only (`0.5`) | 5,615 | 14.46% | 5,613 | 83.07% | 99.96% |

## Overlap on fraud sessions

- caught by both rule-only and ML-only: `3,902`
- caught only by rule-only: `1,103`
- caught only by ML-only: `1,711`
- missed by both: `41`

## What the comparison says

### 1. Rule-only is the clean containment layer

The tuned rule layer is extremely precise:

- precision: `100.00%`

Interpretation:

- rules are appropriate for explicit containment and escalation
- they catch only the clearest downstream misuse sessions

### 2. ML-only adds meaningful behavioural coverage

The narrowed behavioural XGBoost model improves recall materially:

- recall: `83.07%`

while staying almost perfectly precise:

- precision: `99.96%`

Interpretation:

- the project-2 ML layer is adding real value beyond the explicit rules
- it is catching a substantial number of fraud sessions that the rule layer misses

### 3. The two approaches are complementary

The `1,711` fraud sessions caught only by ML-only are the most important result here.

Interpretation:

- rules capture explicit misuse patterns
- ML captures additional behavioural misuse patterns that are not strong enough to encode as direct containment rules

## Recommended hybrid direction

The hybrid policy should preserve:

- rules as hard containment or strong-review triggers
- ML as the layer that broadens fraud capture beyond explicit downstream completions

The next design question is not whether hybrid is needed.

It is:

- what operating target should the post-login hybrid policy optimize for?

## Current conclusion

The justified project position is:

1. keep the tuned rule layer for explicit containment
2. keep the narrowed behavioural ML layer for broader detection
3. design the hybrid layer as a policy combiner rather than a score average
