# Rules Specification

Last updated: 11 April 2026

## Purpose

This document defines the first baseline rule set for the Singpass Login Risk Engine.

The rule layer is the interpretable half of the hybrid detection design:

- rules provide transparent operational logic
- ML will later provide additional pattern capture on top of the same feature table

## Input

The rule layer operates on:

- `generated/login_features.csv`

Each row represents one successful decisive login outcome.

## Version 1 rule set

The first rule set is intentionally small.

It is designed to catch the clearest login-stage risk patterns already visible in the current feature table.

### R01: Fast QR Approval

Intent:

- catch suspiciously fast approval behavior

Logic:

- `login_event_type = qr_login_approved`
- `approval_latency_seconds <= 2.0`

Why:

- fraud rows currently show much lower approval latency than non-fraud rows

### R02: Repeated Rejection Pressure

Intent:

- catch sessions with repeated rejected attempts before eventual success

Logic:

- `session_rejected_login_events_before_login >= 2`

Why:

- this directly maps to the repeated-attempt scenario

### R03: High Attempt Volume Before Success

Intent:

- catch sessions with unusually high request volume before successful login

Logic:

- `session_qr_request_count_before_login >= 4`

Why:

- this is a broader pressure/probing rule than explicit rejection count alone

### R04: Fast Foreign First-Seen Login

Intent:

- catch logins from foreign contexts that are also first-seen for the user

Logic:

- `country != SG`
- `new_country_for_user_flag = 1`
- `approval_latency_seconds <= 2.0`

Why:

- fraud rows are less Singapore-heavy than non-fraud rows in the current synthetic data

### R06: Fast Approval With Novelty

Intent:

- catch suspiciously fast approvals that also occur in a new context

Logic:

- `approval_latency_seconds <= 2.0`
- and at least 1 of:
  - `new_country_for_user_flag = 1`
  - `new_region_for_user_flag = 1`
  - `new_asn_for_user_flag = 1`

Why:

- this is a stronger operational signal than fast approval alone

### R07: Prior Rejection History Plus Success

Intent:

- catch users who recently experienced rejection/failure pressure before current success

Logic:

- `user_prior_rejected_login_count_7d >= 2`

Why:

- fraud rows have meaningfully higher recent rejection history than non-fraud rows

## Rule scoring

Version 1 should use a simple additive score.

Recommended rule weights:

- `R01_fast_qr_approval`: 2
- `R02_repeated_rejection_pressure`: 3
- `R03_high_attempt_volume_before_success`: 3
- `R04_foreign_and_new_country`: 2
- `R06_fast_approval_with_novelty`: 3
- `R07_prior_rejection_history_plus_success`: 2

Recommended output columns:

- `triggered_rule_count`
- `triggered_rules`
- `rule_score`
- `rule_risk_band`
- `rule_review_flag`
- `rule_recommended_action`

## Recommended risk-band mapping

- `0`: `low`
- `1-2`: `medium`
- `3-4`: `high`
- `>=5`: `critical`

Recommended review threshold:

- `rule_score >= 3`

## Expected role of the rule layer

This rule layer is not expected to solve the full login-risk problem.

It should:

- catch the most interpretable suspicious access patterns
- provide transparent reviewer-facing explanations
- serve as a baseline to compare against the later ML model

## Known limitations

- current lifecycle-before-login features are sparse, so there is no strong lifecycle rule yet
- `user_device_link_exists_flag` and `device_used_by_multiple_users_flag` are not useful yet in the current synthetic data
- service sensitivity is currently more valuable as ML context than as a standalone hard rule
- broad stacked-novelty logic was removed from the first tuned baseline because it created too many false positives on legitimate unusual logins
