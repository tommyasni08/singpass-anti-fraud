# Feature Specification

Last updated: 12 April 2026

## Purpose

This document defines the first feature-engineering specification for the Singpass Post-Compromise Monitoring project.

It translates the shared synthetic backend into a session-level monitoring dataset for post-login misuse detection.

The main objective is to create one scored record per monitored post-login session so that project 2 can answer:

- is this authenticated session being used in a suspicious way after access is already obtained?

## Scope

This specification is for project 2 only.

It uses:

- `sessions.csv`
- `events.csv`
- `fraud_labels.csv`
- `services.csv`
- `user_devices.csv`

Version 1 is intentionally limited to post-login misuse detection.

That means:

- the target label comes only from `fraud_stage = post_login_stage`
- login-stage labels remain part of the shared dataset, but are not used as the supervised target here

## Scoring unit

The scoring unit for project 2 is:

- one row per monitored post-login session

This is a deliberate design choice.

Project 2 is a behavioural monitoring problem, not just a single-event classification problem. A session-level view is needed because misuse often appears through:

- event sequence shape
- service switching
- timing between events
- accumulation of moderate-risk actions
- drift from the user’s normal behaviour over the session

The session-level row should therefore summarize what happened after trusted access was established.

## Session inclusion rule

Version 1 session rows should include:

- sessions with a successful login event
- sessions with at least one post-login event after authentication

The post-login event family may include:

- benign `service_usage`
- `consent_data_sharing`
- `digital_signing_authorisation`
- selected `account_device_lifecycle` actions that occur after login

Sessions that end immediately after login without any modeled post-login activity should be excluded from the project-2 feature table.

## Label definition

The target label for the first feature table is:

- `is_fraud_flag` from `fraud_labels.csv`

Restricted to:

- `fraud_stage = post_login_stage`

Joined and aggregated by:

- `session_id`

Recommended output target column:

- `target_post_login_fraud_flag`

Recommended aggregation rule:

- session is labeled fraud if any post-login fraud label exists within that session

## Output table

Recommended output file:

- `post_login_session_features.csv`

Recommended grain:

- one row per monitored session

Recommended mandatory identifier columns:

- `session_id`
- `user_id`
- `device_id`
- `service_id`
- `login_event_id`
- `login_timestamp`
- `target_post_login_fraud_flag`
- `dominant_fraud_scenario`

## Join strategy

The first feature table should be built in this order:

1. start from `sessions.csv`
2. keep only sessions with successful login and modeled post-login activity
3. join all same-session events from `events.csv`
4. join `fraud_labels.csv` restricted to `fraud_stage = post_login_stage`
5. join `services.csv` on the primary session service
6. derive device-link context from `user_devices.csv`
7. derive session-level behavioural aggregates from post-login events
8. derive simple user and device history features from events before the session start timestamp

## Version 1 feature groups

The first implementation should stay simple and behaviourally meaningful.

### 1. Session identity and entry context

Purpose:

- preserve the entry point into the monitored session

Features:

- `login_event_type`
- `login_method`
- `channel`
- `login_hour_of_day`
- `login_country`
- `login_region`
- `login_asn`
- `service_sector_type`
- `service_risk_tier`

Source:

- `sessions.csv`
- login event from `events.csv`
- `services.csv`

### 2. Post-login activity volume

Purpose:

- measure how much happened after access was obtained

Features:

- `post_login_event_count`
- `post_login_duration_seconds`
- `distinct_event_type_count`
- `distinct_service_count_in_session`
- `sensitive_event_count`
- `benign_service_usage_count`

Source:

- `events.csv`

### 3. Sequence and timing behaviour

Purpose:

- capture whether the session progresses unusually after login

Features:

- `time_to_first_post_login_event_seconds`
- `time_to_first_sensitive_event_seconds`
- `time_to_first_service_switch_seconds`
- `max_event_burst_5m`
- `service_switch_count`
- `sensitive_event_after_sensitive_event_flag`

Source:

- `events.csv`

### 4. Consent and signing behaviour

Purpose:

- capture downstream approvals and authorisations that matter in misuse scenarios

Features:

- `consent_event_count`
- `consent_granted_count`
- `sign_event_count`
- `sign_completed_count`
- `has_any_consent_granted_flag`
- `has_any_sign_completed_flag`
- `first_time_consent_flow_for_user_flag`
- `first_time_sign_flow_for_user_flag`

Source:

- `events.csv`

### 5. Service-usage novelty

Purpose:

- detect unusual downstream service behaviour even when the login itself succeeded

Features:

- `first_time_service_access_in_session_flag`
- `service_used_by_user_last_30d_flag`
- `service_usage_count_by_user_30d`
- `rare_service_access_flag`
- `high_risk_service_access_flag`

Source:

- `events.csv`
- `services.csv`

### 6. Behavioural consistency

Purpose:

- compare the current session against the user’s recent baseline

Features:

- `user_prior_monitored_session_count_30d`
- `user_prior_sensitive_session_count_30d`
- `user_prior_distinct_services_30d`
- `user_prior_avg_post_login_event_count_30d`
- `user_prior_avg_session_duration_seconds_30d`
- `session_event_count_deviation_from_user_avg`
- `session_duration_deviation_from_user_avg`

Source:

- `events.csv`
- derived session history

### 7. Device and account-state context

Purpose:

- detect whether the session is running in a context that recently changed or degraded

Features:

- `user_device_link_exists_flag`
- `is_primary_device_flag`
- `trust_status`
- `days_since_device_linked`
- `days_since_user_device_last_seen`
- `recent_lifecycle_change_before_session_flag`
- `recent_contact_detail_update_before_session_flag`
- `recent_app_reinstall_before_session_flag`

Source:

- `user_devices.csv`
- `events.csv`

## Null and default handling

Session-level monitoring will still contain missing values, but nulls must be handled by meaning.

### Use `0` when the count or duration is truly absent

Examples:

- `consent_granted_count = 0`
- `sign_completed_count = 0`
- `service_switch_count = 0`

### Keep `null` when no valid historical anchor exists

Examples:

- `session_duration_deviation_from_user_avg`
- `session_event_count_deviation_from_user_avg`
- `days_since_user_device_last_seen`

Reason:

- first-observed or no-history sessions are different from zero-deviation sessions

### Use explicit missing flags when useful

Examples:

- `session_duration_deviation_missing_flag`
- `user_history_missing_flag`

### Use `unknown` for categorical values only when needed

Examples:

- missing trust status
- missing sector or risk tier in malformed synthetic rows

## Leakage control

Project 2 is allowed to use post-login behaviour, but it must still avoid future leakage outside the monitored session.

Allowed:

- events within the same session after login
- user history strictly before session start

Not allowed:

- events from later sessions
- labels from future activity
- user behaviour that occurs after the monitored session ends

## First implementation goal

The first implementation should aim to produce a defensible session-level monitoring table that is strong enough for:

- a first rule-based monitoring baseline
- a first ML baseline
- a later hybrid containment policy

The first version does not need to solve full user-level case management yet.

The user or account level can be introduced later at the final decisioning layer as an aggregation or escalation step on top of session scores.
