# Rules Specification

Last updated: 12 April 2026

## Purpose

This document defines the first baseline rule set for the Singpass Post-Compromise Monitoring project.

The rule layer is the interpretable half of the project-2 detection design:

- rules provide explicit containment logic
- ML will later provide additional behavioral pattern detection on top of the same session table

## Input

The rule layer operates on:

- `feature_engineering/generated/post_login_session_features.csv`

Each row represents one monitored post-login session.

## Rule design principles

Project 2 rules should not try to recreate project 1 login-risk logic.

They should focus on:

- suspicious downstream actions after trusted access
- unusual accumulation of sensitive actions
- session-level behavior that suggests misuse rather than normal usage
- patterns that are operationally clear enough to justify containment

## Version 1 rule set

The first rule set should stay compact and high-confidence.

### R01: Consent Granted In Session

Intent:

- catch sessions that contain a completed consent grant event

Logic:

- `has_any_consent_granted_flag = 1`

Why:

- in the current synthetic data, consent grant is strongly concentrated in fraud-labelled post-login sessions
- this is a strong candidate for immediate containment or escalation

### R02: Signing Completed In Session

Intent:

- catch sessions that complete a signing flow

Logic:

- `has_any_sign_completed_flag = 1`

Why:

- completed signing is a high-sensitivity downstream action
- in the current synthetic data, sign completion is also strongly concentrated in fraud-labelled sessions

### R03: Stacked Sensitive Activity

Intent:

- catch sessions where one sensitive action is followed by another

Logic:

- `sensitive_event_after_sensitive_event_flag = 1`

Why:

- this is a strong session-shape misuse pattern
- it captures the accumulation of risky behavior, not just a single event

### R04: Sensitive Session With Service Switching

Intent:

- catch sessions that combine sensitive actions with cross-service movement

Logic:

- `sensitive_event_count >= 1`
- `service_switch_count >= 1`
- `benign_service_usage_count = 0`

Why:

- in the current synthetic data, the added no-benign-usage condition makes this a much cleaner misuse pattern
- this is treated as a narrow containment rule rather than a broad novelty rule

### R05: Sensitive Session Without Benign Usage

Intent:

- catch sessions that move directly into sensitive actions without normal browsing or low-risk usage

Logic:

- `sensitive_event_count >= 1`
- `benign_service_usage_count = 0`

Why:

- benign sessions are currently dominated by service-usage events
- fraud sessions are much more likely to contain sensitive actions without that benign pattern

### R06: High-Burst Sensitive Session

Intent:

- catch very short sessions that jump directly into sensitive activity

Logic:

- `sensitive_event_count >= 1`
- `post_login_duration_seconds <= 60`

Why:

- in the current synthetic data, very short sensitive sessions are highly concentrated in fraud-labelled rows
- this is cleaner than the earlier broad burst rule

### R07: First-Time Sensitive Flow

Intent:

- catch sessions where the user enters a sensitive consent or signing flow for the first observed time

Logic:

- `first_time_consent_flow_for_user_flag = 1`
or
- `first_time_sign_flow_for_user_flag = 1`

Why:

- first-time sensitive flows are concentrated in fraud sessions in the current dataset
- this should not be treated as a hard block by itself, but it is useful review context

## Rule scoring

Version 1 should use a simple additive score.

Recommended rule weights:

- `R01_consent_granted_in_session`: 3
- `R02_signing_completed_in_session`: 3
- `R03_stacked_sensitive_activity`: 3
- `R04_sensitive_session_with_service_switching`: 2
- `R05_sensitive_session_without_benign_usage`: 2
- `R06_high_burst_sensitive_session`: 2
- `R07_first_time_sensitive_flow`: 1

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

This rule layer is not expected to solve the full post-login monitoring problem.

It should:

- catch the clearest downstream misuse patterns
- provide explicit containment logic
- serve as a baseline to compare against the later ML model and hybrid policy

## Important caution

Some of the strongest current rule candidates are very close to the post-login target label:

- completed consent
- completed signing
- stacked sensitive activity

That is acceptable for the rule layer because rules are allowed to act on explicit downstream evidence.

The ML layer should be more selective later so the project does not reduce to a learned version of those same near-deterministic signals.

## Known limitations

- the current synthetic data still contains relatively simple post-login journeys, so session complexity is modest
- lifecycle-before-session features are weak in the first generated version
- service risk tier is currently weak by itself and should remain secondary context rather than a standalone high-weight rule
