# Model Comparison

Last updated: 11 April 2026

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
| Hybrid | 4,760 | 12.04% | 3,892 | 88.64% | 81.76% |

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

### 3. The current hybrid policy is only marginally different from ML-only

Current hybrid result:

- review rate: `12.04%`
- recall: `88.64%`
- precision: `81.76%`

Current ML-only at `0.5`:

- review rate: `12.05%`
- recall: `88.70%`
- precision: `81.76%`

Interpretation:

- the current hybrid policy is very close to ML-only
- this means the present policy layer is not yet adding much incremental value over the ML threshold by itself

## Why hybrid is still worth keeping

Even though the current metrics are almost identical to ML-only, hybrid still has a strong product and operational argument:

- rules provide explicit, reviewer-friendly justifications
- rules are better for hard overrides in very clear cases
- ML is better for broad pattern capture
- a policy layer is easier to audit and tune than relying on probability alone

So the current conclusion is not:

- hybrid is unnecessary

The current conclusion is:

- the hybrid policy needs another tuning pass if it is meant to add measurable value beyond ML-only

## Recommended choice right now

If choosing by current metrics alone:

- choose ML-only with a threshold around `0.5` to `0.7`

If choosing by operational design for the portfolio:

- choose hybrid as the target architecture
- but acknowledge that the current hybrid policy still behaves almost the same as ML-only

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

- the current hybrid is heavily driven by the ML layer
- the rules are mostly reinforcing cases that ML already catches

## Decision

The justified portfolio position is:

1. rules are useful and operationally interpretable
2. ML is currently the strongest standalone detector
3. hybrid remains the preferred architecture, but its policy should be tuned further before claiming it meaningfully outperforms ML-only
