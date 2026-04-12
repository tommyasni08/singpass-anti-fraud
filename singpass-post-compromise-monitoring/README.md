# Singpass Post-Compromise Monitoring

This project simulates and scores suspicious post-login behaviour in a Singpass-like identity environment.

The objective is to minimise damage after compromise by monitoring authenticated sessions, detecting downstream misuse early, and escalating containment actions before misuse spreads further.

## Project focus

This is the second project in the two-project anti-fraud portfolio:

- project 1: detect suspicious live login or approval context
- project 2: detect misuse after access is already trusted

This project is intentionally session-level. It asks:

`Now that access exists, is this session being used in a harmful way, and should it be contained?`

## Shared data foundation

The project runs on the same shared synthetic backend as project 1. The main inputs are:

- `users`
- `devices`
- `user_devices`
- `services`
- `sessions`
- `events`
- `fraud_labels`

The scored population is limited to authenticated sessions with at least one modeled post-login event.

## End-to-end pipeline

The implementation is split into four layers:

1. **Feature engineering**
Transforms raw session and event data into a session-level monitoring table.

2. **Rule-based score**
Applies explicit downstream containment rules for high-confidence misuse patterns.

3. **ML-based score**
Uses an XGBoost model for broader behavioural misuse detection with a narrower feature set than the rule layer.

4. **Hybrid score**
Combines rule outputs and ML outputs through a recall-first containment policy.

The project output is an operational containment layer with actions such as:

- `allow`
- `review_due_to_behavioral_risk`
- `manual_review`
- `restrict_or_manual_review`

## Current outputs

- [Project Plan](/Users/tommyasni08/Documents/Projects/singpass-anti-fraud/singpass-post-compromise-monitoring/project_plan.md)
- [Feature Engineering](/Users/tommyasni08/Documents/Projects/singpass-anti-fraud/singpass-post-compromise-monitoring/feature_engineering/README.md)
- [Rule-Based Score](/Users/tommyasni08/Documents/Projects/singpass-anti-fraud/singpass-post-compromise-monitoring/rule_based_score/README.md)
- [ML-Based Score](/Users/tommyasni08/Documents/Projects/singpass-anti-fraud/singpass-post-compromise-monitoring/ml_based_score/README.md)
- [Hybrid Score](/Users/tommyasni08/Documents/Projects/singpass-anti-fraud/singpass-post-compromise-monitoring/hybrid_score/README.md)

Key generated artifacts:

- [Post-Login Session Features](/Users/tommyasni08/Documents/Projects/singpass-anti-fraud/singpass-post-compromise-monitoring/feature_engineering/generated/post_login_session_features.csv)
- [Feature Quality Report](/Users/tommyasni08/Documents/Projects/singpass-anti-fraud/singpass-post-compromise-monitoring/feature_engineering/generated/feature_quality_report.md)
- [Rule Quality Report](/Users/tommyasni08/Documents/Projects/singpass-anti-fraud/singpass-post-compromise-monitoring/rule_based_score/generated/rule_quality_report.md)
- [ML Evaluation Report](/Users/tommyasni08/Documents/Projects/singpass-anti-fraud/singpass-post-compromise-monitoring/ml_based_score/generated/ml_evaluation_report.md)
- [Hybrid Evaluation Report](/Users/tommyasni08/Documents/Projects/singpass-anti-fraud/singpass-post-compromise-monitoring/hybrid_score/generated/hybrid_evaluation_report.md)
- [Model Comparison](/Users/tommyasni08/Documents/Projects/singpass-anti-fraud/singpass-post-compromise-monitoring/hybrid_score/generated/model_comparison.md)

## Current model results

All approaches were evaluated on the same `38,834` monitored sessions, with `6,757` fraud-labelled sessions.

| Approach | Review Rate | Recall | Precision |
| --- | ---: | ---: | ---: |
| Rule-only | 12.89% | 74.07% | 100.00% |
| ML-only (`ml_score >= 0.5`) | 14.46% | 83.07% | 99.96% |
| Hybrid v1 (`rule OR ml_score >= 0.3`) | 18.08% | 99.48% | 95.73% |

## Why the project keeps the hybrid design

Project 2 is a containment problem, so recall matters more than minimizing review volume.

The final hybrid policy keeps:

- rules for explicit downstream misuse and hard containment
- ML for broader behavioural detection beyond direct downstream completion patterns

The most important result is:

- `1,711` fraud sessions were caught by ML-only and missed by the tuned rule layer

That makes the hybrid layer necessary rather than optional.

The selected hybrid operating point prioritizes containment recall:

- review rate: `18.08%`
- recall: `99.48%`
- precision: `95.73%`

## Main technical findings

- A session-level scoring unit is the correct choice for project 2 because misuse appears through sequence shape and accumulation, not just single events.
- The rule layer is intentionally strong and explicit because direct downstream misuse evidence should trigger containment.
- The first ML attempt was too easy because the feature set still contained session-composition shortcuts.
- The final ML baseline became credible only after removing direct label-proxy features and keeping a narrower behavioural feature set.
- The hybrid layer works best as a recall-first policy combiner rather than a score average.

## Scope boundary

This project focuses on session-level post-login monitoring.

It does not yet implement a full user-level case-management layer. User or account-level escalation can be added later on top of session scores as an aggregation or monitoring step.
