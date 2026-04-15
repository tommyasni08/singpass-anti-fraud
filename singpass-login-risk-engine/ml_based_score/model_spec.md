# Model Specification

Last updated: 15 April 2026

## Purpose

This document defines the first ML baseline for the Singpass Login Risk Engine.

The ML layer is the second half of the hybrid detection design:

- rules capture explicit suspicious patterns
- the ML model captures weaker combinations of signals that are not worth hard-coding as rules

## Input

The model consumes:

- `feature_engineering/generated/login_features.csv`

Each row is one successful decisive login outcome with a login-stage target label.

## Baseline design

The first ML baseline should be intentionally simple.

The goal is not to maximize leaderboard-style performance. The goal is to establish:

- a reproducible training/evaluation path
- a baseline fraud probability score
- a comparison point against the rule-based layer

## Current implementation choice

The current project virtual environment provides:

- `scikit-learn`
- `xgboost`

So the first real ML baseline uses:

- XGBoost classifier

Why this is the better choice here:

- the problem is tabular fraud scoring, not text or image modeling
- the current feature table includes nonlinear interaction candidates
- the tuned rule layer already suggests that stacked conditions matter
- gradient-boosted trees are a strong default for this type of data

Scikit-learn matters in this setup for:

- preprocessing pipeline management
- metrics
- future benchmark models such as logistic regression

## Target

Supervised target:

- `target_login_fraud_flag`

## Train / evaluation split

Version 1 uses a deterministic split based on event timestamp ordering:

- earliest 80% of rows by event timestamp -> training set
- latest 20% of rows by event timestamp -> evaluation set

Why:

- this is closer to real fraud deployment than random splitting
- it avoids leaking future patterns backward into training

## Feature selection for baseline

The first baseline uses:

- core numeric features
- selected categorical features after pipeline-based one-hot encoding

Included:

- `approval_latency_seconds`
- `approval_latency_missing_flag`
- `login_hour_of_day`
- `service_supports_myinfo_flag`
- `service_supports_signing_flag`
- `user_device_link_exists_flag`
- `is_primary_device_flag`
- `new_country_for_user_flag`
- `new_region_for_user_flag`
- `new_asn_for_user_flag`
- `session_event_count_before_login`
- `session_failed_login_events_before_login`
- `session_rejected_login_events_before_login`
- `session_qr_request_count_before_login`
- `session_qr_prompt_count_before_login`
- `session_has_lifecycle_event_before_login_flag`
- `session_lifecycle_event_count_before_login`
- `session_has_contact_detail_updated_before_login_flag`
- `user_prior_login_count_7d`
- `user_prior_successful_login_count_7d`
- `user_prior_rejected_login_count_7d`
- `user_prior_distinct_services_30d`
- `user_prior_distinct_countries_30d`
- `user_prior_distinct_asns_30d`
- `days_since_last_successful_login`
- `days_since_last_successful_login_missing_flag`
- `device_prior_login_count_30d`
- `device_prior_distinct_users_30d`
- `device_used_by_multiple_users_flag`
- `first_time_service_for_user_flag`
- `service_used_by_user_last_30d_flag`
- `service_usage_count_by_user_30d`

Deferred from the first baseline:

- raw IDs
- raw IP address
- high-cardinality categorical variables

Reason:

- the first baseline should remain interpretable and operationally lightweight

## Preprocessing and serving design

Project 1 now uses the same production-friendly pattern as project 2:

- `ColumnTransformer`
- `SimpleImputer`
- `OneHotEncoder`
- sklearn `Pipeline`
- XGBoost classifier

Why this was adopted:

- training and API inference should share the same preprocessing contract
- serving should not rely on manually rebuilding dummy columns
- the ML artifact should be loadable directly by the scoring API

This is cleaner than the earlier MVP path that used manual `pandas.get_dummies`.

## Output

The ML baseline should produce:

- predicted fraud probability per login
- binary prediction at a chosen threshold
- evaluation summary on the holdout split

Recommended output columns:

- `event_id`
- `target_login_fraud_flag`
- `ml_score`
- `ml_predicted_flag`
- `split_name`

Serving artifacts:

- `xgb_model.json`
- `serving_pipeline.joblib`
- `serving_metadata.json`

## Evaluation

The first report should include:

- train vs evaluation row counts
- fraud rate by split
- precision at multiple thresholds
- recall at multiple thresholds
- accuracy
- top feature importance

## Role in the hybrid stack

The ML score is not intended to replace rules immediately.

It is intended to answer:

- does the current feature table contain enough predictive signal beyond the hard-coded rules?

The current role of this baseline is:

- compare rule-based score vs ML score
- support threshold analysis against review-rate targets
- feed the final hybrid decision layer
