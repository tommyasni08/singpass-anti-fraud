# Model Specification

Last updated: 12 April 2026

## Purpose

This document defines the first ML baseline for the Singpass Post-Compromise Monitoring project.

The ML layer is the second half of the project-2 detection design:

- rules capture explicit downstream misuse patterns
- the ML model captures broader behavioural misuse patterns at the session level

## Input

The model consumes:

- `feature_engineering/generated/post_login_session_features.csv`

Each row is one monitored post-login session with a post-login target label.

## Baseline design

The first ML baseline should remain narrower than the rule layer.

Reason:

- the rule layer already covers the clearest explicit downstream misuse cases
- several current session features are extremely close to the post-login fraud label
- the ML layer should add behavioural coverage rather than just relearn direct label proxies

## Current implementation choice

The project virtual environment provides:

- `scikit-learn`
- `xgboost`

So the first project-2 ML baseline uses:

- XGBoost classifier

## Target

Supervised target:

- `target_post_login_fraud_flag`

## Train / evaluation split

Version 1 uses a deterministic split based on login timestamp ordering:

- earliest 80% of sessions by `login_timestamp` -> training set
- latest 20% of sessions -> evaluation set

## Feature selection for baseline

The first post-login ML baseline should prioritize behavioural and contextual features.

Included:

- `post_login_duration_seconds`
- `distinct_service_count_in_session`
- `time_to_first_post_login_event_seconds`
- `time_to_first_service_switch_seconds`
- `time_to_first_service_switch_missing_flag`
- `max_event_burst_5m`
- `service_switch_count`
- `service_used_by_user_last_30d_flag`
- `service_usage_count_by_user_30d`
- `rare_service_access_flag`
- `high_risk_service_access_flag`
- `user_prior_monitored_session_count_30d`
- `user_prior_sensitive_session_count_30d`
- `user_prior_distinct_services_30d`
- `user_prior_avg_post_login_event_count_30d`
- `user_prior_avg_session_duration_seconds_30d`
- `session_event_count_deviation_from_user_avg`
- `session_event_count_deviation_missing_flag`
- `session_duration_deviation_from_user_avg`
- `session_duration_deviation_missing_flag`
- `login_hour_of_day`
- `recent_lifecycle_change_before_session_flag`
- `recent_contact_detail_update_before_session_flag`
- `recent_app_reinstall_before_session_flag`
- `service_sector_type`
- `service_risk_tier`
- `login_method`
- `login_country`
- `trust_status`

Explicitly excluded from the first ML baseline:

- `post_login_event_count`
- `distinct_event_type_count`
- `sensitive_event_count`
- `benign_service_usage_count`
- `has_any_consent_granted_flag`
- `has_any_sign_completed_flag`
- `first_time_consent_flow_for_user_flag`
- `first_time_sign_flow_for_user_flag`
- `consent_event_count`
- `sign_event_count`
- `consent_granted_count`
- `sign_completed_count`
- `sensitive_event_after_sensitive_event_flag`
- `time_to_first_sensitive_event_seconds`
- `time_to_first_sensitive_event_missing_flag`

Reason:

- these are useful for explicit rules
- but they are too close to the label for the first behavioural ML baseline
- in the current synthetic data, several of these fields are effectively direct summaries of whether a sensitive downstream action happened at all

## Output

The ML baseline should produce:

- predicted fraud probability per monitored session
- binary prediction at chosen thresholds
- evaluation summary on the holdout split

Recommended output columns:

- `session_id`
- `target_post_login_fraud_flag`
- `ml_score`
- `ml_predicted_flag`
- `split_name`

## Evaluation

The first report should include:

- train vs evaluation row counts
- fraud rate by split
- precision at multiple thresholds
- recall at multiple thresholds
- accuracy
- top feature importance

## Role in the project-2 stack

The ML score is not intended to replace the rule layer.

It is intended to answer:

- does the current session-level feature table contain behavioural signal beyond the explicit downstream rules?

The next step after this baseline is:

- compare rule-based score vs ML score
- decide whether the ML layer adds enough value on the fraud rows missed by rules
- then design a hybrid containment policy
