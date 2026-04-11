# Feature Specification

Last updated: 11 April 2026

## Purpose

This document defines the first feature-engineering specification for the Singpass Login Risk Engine.

It translates the shared synthetic backend into a model-ready login-stage dataset for project 1.

The main objective is to create one scored record per decisive login outcome so that project 1 can answer:

- is this login suspicious enough to intervene now?

## Scope

This specification is for project 1 only.

It uses:

- `sessions.csv`
- `events.csv`
- `fraud_labels.csv`
- `services.csv`
- `user_devices.csv`

Version 1 is intentionally limited to the login-stage problem.

That means:

- the target label comes only from `fraud_stage = login_stage`
- post-login labels remain part of the shared dataset, but are not used as the supervised target here

## Scoring unit

The scoring unit for project 1 is:

- one row per decisive login event

In the current generated dataset, the decisive login event is typically one of:

- `app_login_success`
- `qr_login_approved`
- `qr_login_rejected`
- `app_login_failure`

For version 1, the recommended scored subset is:

- successful decisive login outcomes only

This means the first feature table should focus on:

- `app_login_success`
- `qr_login_approved`

Reason:

- the main project question is whether a login that is about to be trusted should be allowed, stepped up, delayed, blocked, or allowed with enhanced monitoring
- rejected or failed attempts are still useful as precursor features, but they are not the main scored unit for the first baseline

## Label definition

The target label for the first feature table is:

- `is_fraud_flag` from `fraud_labels.csv`

Restricted to:

- `fraud_stage = login_stage`

Joined on:

- `event_id`

The output target column should be normalized to:

- `target_login_fraud_flag`

## Output table

Recommended output file:

- `login_features.csv`

Recommended grain:

- one row per scored login event

Recommended mandatory identifier columns:

- `event_id`
- `session_id`
- `user_id`
- `device_id`
- `service_id`
- `event_timestamp`
- `login_event_type`
- `target_login_fraud_flag`
- `fraud_scenario`

## Join strategy

The first feature table should be built in this order:

1. start from `events.csv`
2. keep only scored login events
3. join `fraud_labels.csv` on `event_id` for `fraud_stage = login_stage`
4. join `sessions.csv` on `session_id`
5. join `services.csv` on `service_id`
6. derive device-link context from `user_devices.csv`
7. derive session-level precursor features from all events in the same session
8. derive simple historical features from prior events for the same user or device

## Version 1 feature groups

The first implementation should stay simple and defensible.

### 1. Scored event identity

Purpose:

- preserve the decisive login context

Features:

- `login_event_type`
- `login_method`
- `channel`
- `event_result`
- `approval_latency_seconds`

Source:

- `events.csv`
- `sessions.csv`

### 2. Service context

Purpose:

- capture whether the login is occurring against a more sensitive or unfamiliar service context

Features:

- `service_sector_type`
- `service_risk_tier`
- `service_supports_myinfo_flag`
- `service_supports_signing_flag`

Source:

- `services.csv`

### 3. Device-link context

Purpose:

- capture whether the user-device relationship looks familiar or trusted

Features:

- `user_device_link_exists_flag`
- `is_primary_device_flag`
- `trust_status`
- `days_since_device_linked`
- `days_since_user_device_last_seen`

Source:

- `user_devices.csv`

Notes:

- these should be derived relative to the login event timestamp
- if no matching user-device link exists, the feature row should still be kept and the missing relationship should become signal

### 4. Network and geo context

Purpose:

- preserve raw access context and derive novelty-style features later

Features:

- `country`
- `region`
- `asn`
- `ip_address`

Version 1 derived features:

- `new_country_for_user_flag`
- `new_region_for_user_flag`
- `new_asn_for_user_flag`

Source:

- `events.csv`

Notes:

- full impossible-travel logic can be added later
- version 1 should begin with novelty and presence signals first

### 5. Session-level precursor behaviour

Purpose:

- summarize what happened earlier in the same session before the decisive login event

Features:

- `session_event_count_before_login`
- `session_failed_login_events_before_login`
- `session_rejected_login_events_before_login`
- `session_qr_request_count_before_login`
- `session_qr_prompt_count_before_login`
- `session_has_lifecycle_event_before_or_near_login_flag`
- `session_lifecycle_event_count`
- `session_has_contact_detail_updated_flag`

Source:

- `events.csv`

Why this matters:

- several login-risk scenarios are visible through session sequence shape rather than a single raw event

### 6. Recent user history

Purpose:

- compare the current login against recent user behaviour

Features:

- `user_prior_login_count_7d`
- `user_prior_successful_login_count_7d`
- `user_prior_rejected_login_count_7d`
- `user_prior_distinct_services_30d`
- `user_prior_distinct_countries_30d`
- `user_prior_distinct_asns_30d`
- `days_since_last_successful_login`

Source:

- `events.csv`

Notes:

- all history must be computed strictly from events before the scored event timestamp
- do not leak same-session downstream activity

### 7. Device history

Purpose:

- compare the current login to prior activity on the same device

Features:

- `device_prior_login_count_30d`
- `device_prior_distinct_users_30d`
- `device_used_by_multiple_users_flag`

Source:

- `events.csv`
- `user_devices.csv`

Why this matters:

- relinquished-account and suspicious access cases may show shared-device or device-reuse behaviour

### 8. Service novelty relative to the user

Purpose:

- detect whether the service itself is unusual for the user

Features:

- `first_time_service_for_user_flag`
- `service_used_by_user_last_30d_flag`
- `service_usage_count_by_user_30d`

Source:

- `events.csv`

Notes:

- novelty alone should not be treated as fraud
- this group is valuable mainly when combined with other context

## Features explicitly deferred from version 1

The following are valid later additions, but should not block the first pipeline:

- impossible travel
- precise geo distance
- full user baseline clustering
- graph-based device-user features
- sequence embeddings
- cross-session behavioural drift scores
- post-login usage features

## Null and default handling

Version 1 should keep missingness explicit where it is meaningful.

The goal is not to eliminate nulls everywhere. The goal is to distinguish between:

- true absence of prior information
- expected zero-count behavior
- unavailable or not-applicable values

### 1. Join miss vs real zero

These two cases should not be treated the same.

Example:

- if a user has no matching record in `user_devices.csv` for the current `user_id + device_id`, that means the device-link relationship is missing
- that is different from a linked device whose history-derived count is genuinely zero inside a time window

Handling rule:

- create an explicit existence flag first
- only then derive the dependent numeric fields

Recommended handling:

- `user_device_link_exists_flag`
  - `1` if a matching user-device relationship exists
  - `0` if no relationship exists
- `is_primary_device_flag`
  - use `0` only when a relationship exists and it is not primary
  - if no relationship exists, keep a companion flag and fill the stored value with `0`
- `trust_status`
  - use the actual category if linked
  - otherwise use `unknown`
- `days_since_device_linked`
  - null if no user-device link exists
- `days_since_user_device_last_seen`
  - null if no user-device link exists

Why:

- for version 1, the missing relationship itself is risk signal
- forcing all relationship-derived values to zero would blur “unknown device” and “known device with zero recent activity”

### 2. Count features

Count features should default to zero when the count window is well-defined and no qualifying prior events exist.

Recommended handling:

- `session_event_count_before_login`
- `session_failed_login_events_before_login`
- `session_rejected_login_events_before_login`
- `session_qr_request_count_before_login`
- `session_qr_prompt_count_before_login`
- `session_lifecycle_event_count`
- `user_prior_login_count_7d`
- `user_prior_successful_login_count_7d`
- `user_prior_rejected_login_count_7d`
- `user_prior_distinct_services_30d`
- `user_prior_distinct_countries_30d`
- `user_prior_distinct_asns_30d`
- `device_prior_login_count_30d`
- `device_prior_distinct_users_30d`
- `service_usage_count_by_user_30d`

Handling rule:

- if the window exists and there are no qualifying prior records, use `0`

Why:

- these are true count features
- zero is the correct semantic value when nothing happened before the event

### 3. Boolean flags

Boolean flags should default to `0` only when the underlying condition is definitively false.

Recommended handling:

- `new_country_for_user_flag`
- `new_region_for_user_flag`
- `new_asn_for_user_flag`
- `first_time_service_for_user_flag`
- `service_used_by_user_last_30d_flag`
- `device_used_by_multiple_users_flag`
- `session_has_lifecycle_event_before_or_near_login_flag`
- `session_has_contact_detail_updated_flag`

Handling rule:

- use `1` when the condition is true
- use `0` when the condition is false based on available history

Special case for cold-start users:

- if there is no relevant prior user history at all, novelty-style flags can still safely be set to `1`

Reason:

- for a first observed login, the country, region, ASN, and service are all effectively first-seen values in the synthetic history

This should be documented explicitly in the pipeline so it is not mistaken for a bug later.

### 4. Time-delta features

Time-delta features should remain null when there is no valid anchor event.

Recommended handling:

- `approval_latency_seconds`
- `days_since_device_linked`
- `days_since_user_device_last_seen`
- `days_since_last_successful_login`

Handling rule:

- if the timestamp anchor exists, compute the delta
- if the anchor does not exist, leave the feature null
- add a companion missingness flag when the feature is likely to matter operationally

Recommended companion flags:

- `approval_latency_missing_flag`
- `days_since_last_successful_login_missing_flag`

Why:

- `0` would be misleading for these features
- null correctly means “not observed yet” or “not applicable”

### 5. Raw categorical fields

Categorical fields should use an explicit fallback category rather than dropping rows.

Recommended handling:

- `login_method`
- `channel`
- `country`
- `region`
- `asn`
- `service_sector_type`
- `service_risk_tier`
- `trust_status`

Handling rule:

- if the raw field is missing or not joined successfully, use `unknown`

Why:

- this preserves the row
- it also makes missingness visible to rules or later encoding steps

### 6. Raw identifier-like fields

Some raw columns are useful for traceability or later inspection, but should not be fed directly into a baseline model.

Examples:

- `ip_address`
- `user_id`
- `device_id`
- `service_id`
- `session_id`
- `event_id`

Handling rule:

- keep them in the output dataset
- do not impute them
- treat them as record identifiers or audit fields, not baseline predictive features

### 7. Current recommended null policy summary

Use null:

- time-delta features without a valid anchor
- relationship-derived numeric fields when the relationship does not exist

Use zero:

- count features with no qualifying prior records
- boolean flags that are definitively false

Use `unknown`:

- categorical fields with missing or unavailable values

Add explicit missingness flags:

- when null itself may carry useful signal, especially for latency or prior-history anchors

## Leakage constraints

The first feature pipeline must avoid post-login leakage.

Strict rules:

- do not use post-login events as project 1 features
- do not use `post_login_stage` labels
- do not use downstream damage flags
- do not summarize future events after the scored login timestamp

This is especially important because the shared synthetic dataset contains both project 1 and project 2 signals.

## Recommended implementation order

### Phase 1

Build the smallest usable login feature table with:

- scored login events
- login-stage label join
- session join
- service join
- user-device-link join

### Phase 2

Add session-level precursor counts:

- prior requests
- prior rejections
- lifecycle events near login

### Phase 3

Add simple historical user and device windows:

- prior user login counts
- service novelty
- country and ASN novelty

### Phase 4

Freeze the first modeling dataset and inspect:

- row counts
- class balance
- feature null rates
- scenario distribution

Only after that should project 1 move into:

- baseline rules
- baseline model training

## Current plan for this step

The implementation plan for project 1 feature engineering is:

1. identify the decisive login events to score
2. build the first extracted login target table from `events + fraud_labels`
3. join session, service, and user-device context
4. add session-level precursor features from same-session prior events
5. export the first modeling table and inspect it before adding more history

This order keeps the first pass narrow and testable.

## Assumptions to keep explicit

The first feature pass will assume:

- successful decisive login outcomes are the primary scoring unit
- failed or rejected login events are precursor context, not the main target rows
- `user_devices.csv` is the main source of trust-link context
- service sensitivity is represented through static service attributes, not a separate model

## One decision to confirm before coding

My recommendation is:

- score only successful decisive login outcomes in version 1

That means:

- `app_login_success`
- `qr_login_approved`

and use rejected or failed events only as supporting context.

This is the cleaner operational framing for a live login risk engine.

If you want, I can proceed on that assumption and start building the first feature dataset generator next.
