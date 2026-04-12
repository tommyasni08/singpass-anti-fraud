# Singpass Login Risk Engine

This project simulates and scores suspicious live login activity in a Singpass-like authentication environment.

The objective is to minimise compromise of trusted identity accounts at the point of login, before access can be used for downstream abuse such as fraudulent financial account creation, account relinquishment, or deceptive approval flows.

## Project focus

This is the first project in a two-project anti-fraud portfolio:

- project 1: detect suspicious login or approval context in real time
- project 2: monitor post-login behaviour and contain downstream misuse

This project is intentionally limited to the live authentication stage. It asks:

`Should this successful login be trusted, stepped up, monitored, or blocked?`

## Shared data foundation

The project runs on the shared synthetic backend designed for the full portfolio. The main inputs are:

- `users`
- `devices`
- `user_devices`
- `services`
- `sessions`
- `events`
- `fraud_labels`

The scored population is limited to successful decisive login outcomes:

- `app_login_success`
- `qr_login_approved`

Supporting login context is derived from session history, device relationships, service context, and prior user behaviour.

## End-to-end pipeline

The implementation is split into four layers:

1. **Feature engineering**
Transforms raw session and event data into a scored login feature table.

2. **Rule-based score**
Applies explicit anti-fraud rules for high-confidence cases such as repeated rejection pressure and fast suspicious approvals.

3. **ML-based score**
Uses an XGBoost model for broader pattern detection across tabular login features.

4. **Hybrid score**
Combines rule outputs and ML outputs through a policy layer tuned to operational targets.

The project output is not just a fraud probability. It is an operational decision layer with actions such as:

- `allow`
- `allow_with_monitoring`
- `step_up`
- `step_up_or_manual_review`
- `block_or_manual_review`

## Current outputs

- [Project Plan](/Users/tommyasni08/Documents/Projects/singpass-anti-fraud/singpass-login-risk-engine/project_plan.md)
- [Feature Engineering](/Users/tommyasni08/Documents/Projects/singpass-anti-fraud/singpass-login-risk-engine/feature_engineering/README.md)
- [Rule-Based Score](/Users/tommyasni08/Documents/Projects/singpass-anti-fraud/singpass-login-risk-engine/rule_based_score/README.md)
- [ML-Based Score](/Users/tommyasni08/Documents/Projects/singpass-anti-fraud/singpass-login-risk-engine/ml_based_score/README.md)
- [Hybrid Score](/Users/tommyasni08/Documents/Projects/singpass-anti-fraud/singpass-login-risk-engine/hybrid_score/README.md)

Key generated artifacts:

- [Login Features](/Users/tommyasni08/Documents/Projects/singpass-anti-fraud/singpass-login-risk-engine/feature_engineering/generated/login_features.csv)
- [Feature Quality Report](/Users/tommyasni08/Documents/Projects/singpass-anti-fraud/singpass-login-risk-engine/feature_engineering/generated/feature_quality_report.md)
- [Rule Quality Report](/Users/tommyasni08/Documents/Projects/singpass-anti-fraud/singpass-login-risk-engine/rule_based_score/generated/rule_quality_report.md)
- [ML Evaluation Report](/Users/tommyasni08/Documents/Projects/singpass-anti-fraud/singpass-login-risk-engine/ml_based_score/generated/ml_evaluation_report.md)
- [Hybrid Evaluation Report](/Users/tommyasni08/Documents/Projects/singpass-anti-fraud/singpass-login-risk-engine/hybrid_score/generated/hybrid_evaluation_report.md)
- [Model Comparison](/Users/tommyasni08/Documents/Projects/singpass-anti-fraud/singpass-login-risk-engine/hybrid_score/generated/model_comparison.md)

## Current model results

All approaches were evaluated on the same `39,538` successful login rows, with `4,391` fraud-labelled rows.

| Approach | Review Rate | Recall | Precision |
| --- | ---: | ---: | ---: |
| Rule-only | 10.81% | 78.05% | 80.14% |
| ML-only (`ml_score >= 0.5`) | 12.05% | 88.70% | 81.76% |
| Hybrid v3 | 10.46% | 80.96% | 85.93% |

## Why the project keeps the hybrid design

ML-only is currently the strongest pure detector on raw recall. But the final project design keeps the hybrid architecture because it is operationally easier to justify and tune:

- rules provide explicit, reviewer-friendly triggers
- ML captures softer fraud patterns that fixed rules miss
- the hybrid policy can be tuned against operational constraints such as review rate and precision

The final tuned hybrid policy was selected against this operating target:

- keep review rate under `12%`
- maximize recall
- keep precision above `85%`

The final `hybrid v3` operating point achieves:

- review rate: `10.46%`
- recall: `80.96%`
- precision: `85.93%`

This makes the hybrid layer the preferred decisioning output for the project, even though ML-only remains the strongest standalone detector.

## Main technical findings

- `approval_latency_seconds` is the strongest single feature in the current synthetic environment.
- Repeated rejection pressure and high attempt volume are the strongest high-confidence rule patterns.
- XGBoost is a better fit than a linear baseline for this tabular fraud problem because feature interactions matter.
- The hybrid layer works best as a policy combiner, not as a simple average of rule and ML scores.

## Scope boundary

This project stops at the point of live authentication.

It does not try to fully detect downstream misuse after access is granted. That is handled by the second project in the portfolio: post-compromise monitoring and damage containment.
