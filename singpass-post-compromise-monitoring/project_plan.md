# Singpass Post-Compromise Monitoring

Last updated: 8 April 2026

## Project Goal

This project is designed to detect suspicious behaviour after Singpass access has already been obtained.

Its objective is to minimise damage after compromise through active monitoring, early misuse detection, and downstream containment.

The project assumes that prevention at login will never be perfect. Some suspicious or harmful access will still get through. The purpose of this project is to detect what happens next and reduce the impact before the abuse becomes more severe.

## How this project fits the prerequisite layer

This project is built on the same shared prerequisite design as project 1:

- initial product understanding in `initial_research`
- shared event universe in `singpass_event_taxonomy`
- shared minimum viable schema in `data_schema`
- shared backend relationships in `backend_table_design`
- shared scenario universe in `shared_simulation_scenarios`

This means project 2 does not create a separate synthetic environment. It uses the same users, devices, services, sessions, and events as project 1, but focuses on the post-login and downstream-usage slice of that environment.

## Why this project matters

The research narrowed the most relevant Singpass abuse patterns to:

- fraudulent account creation in downstream financial services
- sale or relinquishment of Singpass accounts or credentials
- stolen or deceptively obtained Singpass credentials

These abuse patterns are not fully observable at login alone.

In many cases, the strongest evidence appears after access is obtained, when the attacker begins to use Singpass as a trusted gateway into downstream actions. That is why a second project is needed.

Project 2 is therefore responsible for answering:

- is this account being used in a suspicious way after authentication?
- does the behaviour suggest downstream abuse rather than ordinary user activity?
- what should be restricted, flagged, or contained next?

## Primary problem statement

How can suspicious post-login behaviour be detected early enough to minimise downstream misuse of a compromised, relinquished, or deceptively accessed Singpass account?

The monitoring system should support responses such as:

- flag for review
- increase monitoring level
- restrict high-risk actions
- hold or delay sensitive downstream activity
- escalate for investigation

The goal is not simply to label a session as fraudulent. The goal is to contain damage after prevention has already been partially bypassed.

## Relationship to project 1

The separation between the two projects is:

- project 1 asks: `Is this login or approval context suspicious enough to intervene now?`
- project 2 asks: `After access is obtained, is the account being misused and how should damage be contained?`

Project 1 focuses on pre-access or at-access risk.

Project 2 focuses on:

- post-login behaviour
- downstream usage of trusted identity access
- active monitoring and containment

## Project scope

This project focuses on what happens after login or after trusted access is already established.

The main event families are:

- `login_authentication`, as the entry point into a session
- `consent_data_sharing`
- `digital_signing_authorisation`
- `account_device_lifecycle`

Depending on the final shared simulation design, selected `recovery` events may also be useful as supporting context, but they are not required for version 1.

In practical terms, project 2 is designed to detect misuse such as:

- suspicious downstream financial account-enablement behaviour
- sustained operation of a sold or relinquished Singpass account
- malicious or manipulated post-login approvals, consent, or signing activity

## Main abuse patterns this project covers

### 1. Fraudulent account creation in downstream financial services

This is the clearest downstream misuse case.

The attacker obtains Singpass access, then uses that trusted identity access to open, verify, or enable financial accounts that can later support scam activity.

### 2. Sold or relinquished Singpass account operation

The attacker is not merely logging in once. They are operating the account as if it were their own.

The post-login behaviour becomes important because the strongest signal may be sustained behavioural inconsistency rather than a single suspicious login event.

### 3. Stolen or deceptively obtained credentials used for downstream misuse

The initial access may come from stolen credentials, scam coaching, or manipulated approval.

What matters in project 2 is whether that access is followed by suspicious downstream actions that the legitimate user would not normally perform.

## Core fraud scenarios to monitor

The first version should include both legitimate and suspicious post-login behaviour.

### 1. Normal post-login service usage

- a real user logs in and uses familiar services normally
- no unusual consent, signing, or service-access patterns appear
- session behaviour is consistent with the user's historical baseline

This scenario provides the normal baseline for post-authentication behaviour.

### 2. Legitimate first-time or infrequent service usage

- a real user accesses a service they do not use often
- the behaviour is unusual, but still coherent and legitimate
- session sequence remains reasonable even if novelty is present

This scenario creates realistic false-positive pressure for project 2.

### 3. Downstream financial account-enablement behaviour

- the user gains or appears to gain valid Singpass access
- downstream actions suggest account opening, financial onboarding, or financial-service enablement behaviour
- the sequence is unusual relative to the user's history

This scenario maps directly to the fraudulent financial account creation abuse pattern.

### 4. Sustained relinquished-account operation

- login may appear technically valid
- repeated sessions over time show behavioural drift from the legitimate user's baseline
- accessed services, timing, device context, or usage pattern suggest the account is being operated by a different party

This scenario maps directly to sold or relinquished Singpass account misuse.

### 5. Post-login deceptive consent or approval misuse

- access is obtained
- the user or session proceeds into suspicious approval, consent, or authorisation behaviour
- actions appear technically valid but inconsistent with the user's normal journey

This scenario captures the post-login continuation of stolen or deceptively obtained credentials.

### 6. Suspicious high-risk sequence after authentication

- the user logs in
- shortly after, the session moves through an unusual chain of service access, consent, signing, or lifecycle changes
- the individual events may not each look extreme, but the combined sequence is suspicious

This scenario is important because post-compromise misuse often appears as a sequence rather than a single isolated event.

## Data foundation for the project

This project uses the same shared backend as project 1.

The main tables used in version 1 are:

- `users`
- `devices`
- `user_devices`
- `services`
- `sessions`
- `events`
- `fraud_labels`

The main analytical units in project 2 are:

- sessions
- post-login event sequences
- user-level and device-level behaviour over time

## Event types most relevant to project 2

Project 2 should monitor a broader set of events than project 1.

The most relevant event types are expected to include:

- app_login_success
- qr_login_approved
- consent_request_presented
- consent_granted
- consent_rejected
- consent_cancelled
- myinfo_data_access_completed
- sign_request_initiated
- sign_document_viewed
- sign_approval_prompt
- sign_approved
- sign_completed
- device_changed
- app_reinstalled
- passcode_reset
- contact_detail_updated

These events are relevant because the downstream misuse signal often lies in what happens after authentication, not only in how the authentication happened.

## Feature engineering direction

The monitoring system should derive features at the session, sequence, and behaviour level.

Initial feature groups:

### 1. Session progression features

- time_from_login_to_first_sensitive_event
- number_of_sensitive_events_in_session
- service_switch_count_in_session
- session_duration
- session_event_count

### 2. Service-usage novelty features

- first_time_service_access_flag
- rare_service_access_flag
- high_risk_service_access_flag
- first_time_consent_flow_flag
- first_time_signing_flow_flag

### 3. Behavioural consistency features

- deviation_from_historical_service_mix
- deviation_from_historical_session_timing
- deviation_from_historical_event_sequence
- sustained_access_pattern_shift

### 4. Device and account-state features

- session_on_recently_changed_device_flag
- recent_app_reinstall_flag
- recent_contact_detail_change_flag
- device_shared_across_users_flag

### 5. Sequence-risk features

- login_then_sensitive_action_short_gap
- unusual_consent_then_service_sequence
- unusual_signing_sequence
- repeated_high_risk_session_pattern

## Detection approach

The project should use a layered monitoring design.

### 1. Rule-based monitoring layer

Rules provide a first level of interpretable post-login detection.

Examples:

- first-time high-risk service access shortly after login
- multiple sensitive events in an unusually short session
- repeated access to unfamiliar services across sessions
- suspicious consent or signing sequence after access is obtained

### 2. Behavioural scoring layer

A model or anomaly score can combine multiple weak behavioural signals into a post-compromise risk score.

Recommended first model direction:

- a tabular model on session-level aggregated features

Reason:

- practical for a first version
- easier to explain than a more advanced sequence model
- sufficient to demonstrate active monitoring design

### 3. Containment decision layer

The project should map monitoring outcomes to operational actions such as:

- continue monitoring
- escalate for review
- restrict or hold sensitive actions
- flag account for investigation

This is important because project 2 is about damage containment, not only detection.

## Evaluation approach

Project 2 should be evaluated using measures that reflect monitoring quality and containment value.

Relevant views include:

- precision
- recall
- false positive rate
- detection delay
- session-level recall
- account-level recall
- scenario-level confusion matrix

Important business framing:

- how quickly suspicious downstream behaviour is detected
- how many harmful sessions are flagged before damage escalates
- how often legitimate but unusual activity is incorrectly escalated

## Version 1 deliverables

The first version of the project should include:

### 1. Post-login event simulation layer

Extends the shared synthetic environment with session-level downstream behaviour.

### 2. Monitoring feature pipeline

Builds session-level and sequence-level behavioural features.

### 3. Rule-based monitoring baseline

Applies interpretable rules to suspicious post-login behaviour.

### 4. Behavioural scoring model

Produces a session-level or account-level misuse risk score.

### 5. Monitoring dashboard or reviewer console

Displays suspicious sessions, triggered signals, and recommended containment actions.

## Suggested repository structure

```text
singpass-post-compromise-monitoring/
├── data/
├── notebooks/
├── src/
│   ├── simulation/
│   ├── features/
│   ├── rules/
│   ├── models/
│   ├── monitoring/
│   └── utils/
├── app/
├── outputs/
├── tests/
├── project_plan.md
└── README.md
```

## Why this project matters even if project 1 exists

Project 1 reduces the chance that suspicious access is allowed.

Project 2 is still needed because:

- not all suspicious logins will be blocked
- some abuse becomes clear only after behaviour unfolds
- sustained misuse of a compromised or relinquished account may not be obvious from one login event alone

This makes project 2 a necessary complement to project 1 rather than a duplicate.

## Conclusion

This project is the post-login monitoring and damage-containment layer of the Singpass anti-fraud portfolio.

It shares the same synthetic data backbone as project 1, but it shifts the analytical focus from suspicious access to suspicious usage after access is obtained. Together, the two projects cover both prevention at login and containment after compromise.
