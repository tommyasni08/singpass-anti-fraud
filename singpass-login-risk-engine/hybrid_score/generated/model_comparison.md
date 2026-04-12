# Model Comparison

Last updated: 12 April 2026

## Purpose

This document compares the three current login-risk approaches on the same scored login population:

- rule-only
- ML-only
- hybrid

The goal is to justify which approach should be preferred at the current project stage.

## Comparison basis

All three approaches are evaluated on the same `39,538` successful decisive login rows.

Total fraud rows:

- `4,391`

Operational definitions used for comparison:

- rule-only: `rule_review_flag = 1` which corresponds to `rule_score >= 3`
- ML-only: `ml_score >= 0.5`
- hybrid: `hybrid_review_flag = 1`

## Summary table

| Approach | Review Rows | Review Rate | Fraud Caught | Recall | Precision |
| --- | ---: | ---: | ---: | ---: | ---: |
| Rule-only | 4,276 | 10.81% | 3,427 | 78.05% | 80.14% |
| ML-only (`0.5`) | 4,764 | 12.05% | 3,895 | 88.70% | 81.76% |
| Hybrid v3 | 4,137 | 10.46% | 3,555 | 80.96% | 85.93% |

Additional ML-only reference points:

| ML Threshold | Review Rows | Review Rate | Fraud Caught | Recall | Precision |
| --- | ---: | ---: | ---: | ---: | ---: |
| `0.3` | 4,909 | 12.42% | 3,935 | 89.62% | 80.16% |
| `0.5` | 4,764 | 12.05% | 3,895 | 88.70% | 81.76% |
| `0.7` | 4,744 | 12.00% | 3,881 | 88.39% | 81.81% |

## What the comparison says

### 1. Rule-only is the most conservative

Rule-only sends the fewest rows to review:

- `10.81%` review rate

It also has the lowest recall:

- `78.05%`

Interpretation:

- the tuned rules are strong and precise
- but rules alone still miss too many fraud cases

### 2. ML-only is currently the strongest pure performer

At `ml_score >= 0.5`, ML-only delivers:

- higher recall than rules
- slightly higher precision than rules
- only a modest increase in review rate

Interpretation:

- on the current synthetic dataset, the XGBoost model captures more fraud than the rule layer without paying a precision penalty

### 3. Hybrid is now a distinct operating point

Current hybrid v3 result:

- review rate: `10.46%`
- recall: `80.96%`
- precision: `85.93%`

Current ML-only at `0.5`:

- review rate: `12.05%`
- recall: `88.70%`
- precision: `81.76%`

Interpretation:

- ML-only still wins on raw recall
- hybrid v3 trades some recall for a lower review rate and materially better precision
- this makes hybrid a more defensible operational decision layer under the stated target

## Why hybrid is still worth keeping

Even though ML-only remains the strongest standalone detector on recall, hybrid still has the stronger product and operational argument:

- rules provide explicit, reviewer-friendly justifications
- rules are better for hard overrides in very clear cases
- ML is better for broad pattern capture
- a policy layer is easier to audit and tune than relying on probability alone

So the current conclusion is not:

- hybrid is unnecessary

The current conclusion is:

- hybrid should be treated as the final decision policy when precision and review-rate constraints matter

## Recommended choice right now

If choosing by recall alone:

- choose ML-only with a threshold around `0.5` to `0.7`

If choosing by operational design for the portfolio:

- choose hybrid v3 as the target architecture
- acknowledge that ML-only remains the strongest standalone detector when review-rate and precision constraints are relaxed

That is the most honest justification:

- ML-only currently wins on raw performance
- hybrid is still the better system design
- the hybrid policy should be refined so the rules contribute more than explanation alone

## Evidence for overlap

Among fraud rows:

- `3,427` were caught by all three approaches
- only `3` fraud rows were caught by ML-only and missed by both rule-only and hybrid
- `496` fraud rows were missed by all three

Interpretation:

- hybrid is still heavily informed by the ML layer
- the tuned rule layer now contributes more clearly through the final policy thresholds and hard-trigger pockets

## Decision

The justified portfolio position is:

1. rules are useful and operationally interpretable
2. ML is currently the strongest standalone detector
3. hybrid v3 is the preferred architecture when the operating goal requires review rate under `12%` and precision above `85%`
