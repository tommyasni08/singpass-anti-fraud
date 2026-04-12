# Feature Quality Report

Last updated: 12 April 2026

## Dataset summary

- rows: 38,834
- fraud rows: 6,757
- non-fraud rows: 32,077
- fraud rate: 0.1740

## Scenario distribution

- `legitimate_first_time_or_infrequent_service_usage`: 2,025
- `legitimate_travel_or_device_change_login`: 3,956
- `normal_returning_login_and_normal_usage`: 26,096
- `relinquished_account_access_and_operation`: 1,556
- `remote_control_or_device_compromise_access`: 1,606
- `social_engineering_or_malicious_approval`: 2,436
- `suspicious_downstream_misuse_after_successful_access`: 1,159

## Null-rate summary

- `time_to_first_sensitive_event_seconds`: 28,121 null/blank values (72.41%)
- `time_to_first_service_switch_seconds`: 31,716 null/blank values (81.67%)
- `user_prior_avg_post_login_event_count_30d`: 12,675 null/blank values (32.64%)
- `user_prior_avg_session_duration_seconds_30d`: 12,675 null/blank values (32.64%)
- `session_event_count_deviation_from_user_avg`: 12,675 null/blank values (32.64%)
- `session_duration_deviation_from_user_avg`: 12,675 null/blank values (32.64%)
- `days_since_user_device_last_seen`: 0 null/blank values (0.00%)

## Inspection summary

- The current table is session-level and therefore suitable for behavioural monitoring rather than single-event scoring.
- Post-login activity volume, sensitive action counts, and burstiness are now available for downstream rules and ML.
- Historical baseline features are expected to contain meaningful nulls for early observed sessions with limited prior history.
- The current table is strong enough to proceed to the rule layer, but some session features are currently too close to the target label to be treated as high-value ML features without caution.

## Numeric feature inspection

- `post_login_event_count`
  fraud mean/median: 1.47 / 1.00
  non-fraud mean/median: 1.12 / 1.00
- `sensitive_event_count`
  fraud mean/median: 1.23 / 1.00
  non-fraud mean/median: 0.12 / 0.00
- `benign_service_usage_count`
  fraud mean/median: 0.24 / 0.00
  non-fraud mean/median: 1.00 / 1.00
- `service_switch_count`
  fraud mean/median: 0.94 / 0.00
  non-fraud mean/median: 0.25 / 0.00
- `consent_event_count`
  fraud mean/median: 0.38 / 0.00
  non-fraud mean/median: 0.00 / 0.00
- `sign_event_count`
  fraud mean/median: 0.38 / 0.00
  non-fraud mean/median: 0.00 / 0.00
- `session_event_count_deviation_from_user_avg`
  fraud mean/median: 0.28 / 0.00
  non-fraud mean/median: -0.06 / 0.00
- `session_duration_deviation_from_user_avg`
  fraud mean/median: 14.82 / 0.00
  non-fraud mean/median: -4.02 / 0.00

## Boolean feature inspection

- `has_any_consent_granted_flag`: fraud positive rate 12.45%, non-fraud positive rate 0.00%
- `has_any_sign_completed_flag`: fraud positive rate 13.39%, non-fraud positive rate 0.00%
- `first_time_consent_flow_for_user_flag`: fraud positive rate 35.07%, non-fraud positive rate 0.00%
- `first_time_sign_flow_for_user_flag`: fraud positive rate 35.24%, non-fraud positive rate 0.00%
- `time_to_first_sensitive_event_missing_flag`: fraud positive rate 0.00%, non-fraud positive rate 87.67%
- `time_to_first_service_switch_missing_flag`: fraud positive rate 53.20%, non-fraud positive rate 87.67%
- `sensitive_event_after_sensitive_event_flag`: fraud positive rate 23.03%, non-fraud positive rate 0.00%
- `high_risk_service_access_flag`: fraud positive rate 33.40%, non-fraud positive rate 32.99%
- `recent_lifecycle_change_before_session_flag`: fraud positive rate 4.93%, non-fraud positive rate 5.05%

## Categorical feature inspection

- `login_country`
  fraud top values: SG (63.95%), MY (12.39%), TH (11.85%), ID (11.81%)
  non-fraud top values: SG (87.66%), TH (4.14%), ID (4.11%), MY (4.08%)
- `trust_status`
  fraud top values: trusted (80.23%), new (9.41%), stale (7.41%), revoked (2.95%)
  non-fraud top values: trusted (80.19%), new (9.53%), stale (7.29%), revoked (3.00%)
- `service_risk_tier`
  fraud top values: low (41.88%), high (33.40%), medium (24.72%)
  non-fraud top values: low (41.81%), high (32.99%), medium (25.20%)

## What the current table is good for

- The table is already strong for a first rule-based monitoring layer.
- Sensitive downstream actions are highly visible at the session level.
- Benign service-usage sessions are clearly separated from sessions containing consent, signing, or stacked sensitive behaviour.
- Burstiness, service switching, and session-level accumulation are now represented directly, which is necessary for project 2.

## Main caution for ML design

Several current features are extremely close to the target label:

- `has_any_consent_granted_flag`
- `has_any_sign_completed_flag`
- `first_time_consent_flow_for_user_flag`
- `first_time_sign_flow_for_user_flag`
- `time_to_first_sensitive_event_missing_flag`
- `sensitive_event_after_sensitive_event_flag`

This is not a data leak across sessions, but it is still a modeling shortcut.

Why:

- the session label is defined from post-login fraud events inside the same session
- some of these features are direct summaries of those same decisive events
- this will make the first ML model look stronger than a real earlier-warning monitoring model

## Implication for the next steps

For the rule layer:

- these strong features are still useful
- they can support explicit containment rules for suspicious consent, signing, or stacked sensitive behaviour

For the ML layer:

- we should be selective
- keep some direct post-login indicators for version 1, but avoid building the entire model on near-deterministic label proxies
- prioritize broader behavioural features such as:
  - `post_login_event_count`
  - `sensitive_event_count`
  - `benign_service_usage_count`
  - `service_switch_count`
  - `max_event_burst_5m`
  - session deviation from user baseline
  - login-country and session-context novelty

## Recommended next move

- proceed to the project-2 rule layer first
- treat the current direct post-login indicators as high-confidence rule candidates
- then define a narrower ML feature set that relies more on behavioural pattern features than on direct label proxies
