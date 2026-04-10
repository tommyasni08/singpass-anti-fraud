# Singpass Login Risk Engine

Last updated: 8 April 2026

## Project Goal

This project is designed to simulate and detect suspicious login or approval activity in a Singpass-like authentication environment.

Its objective is to build a real-time risk engine that helps minimise compromise of accounts at the point of live login.

The project is intentionally framed around a high-trust identity system rather than a generic consumer application. The core challenge is not fake-account creation or direct wallet loss inside Singpass. The more relevant problem for this project is identifying suspicious authentication journeys before access is trusted.

## How this project fits the prerequisite layer

This project is built on the shared prerequisite design already defined for the portfolio:

- initial product understanding in `initial_research`
- shared event universe in `singpass_event_taxonomy`
- shared minimum viable schema in `data_schema`
- shared backend relationships in `backend_table_design`

This means the project does not create a separate synthetic world for login risk alone. It uses the shared backend environment and focuses on the login and pre-login slice of that environment.

## Why this project matters

Based on the updated research and recent SPF materials, the most relevant abuse patterns for this project are:

- fraudulent account creation in downstream financial services
- sale or relinquishment of Singpass accounts or credentials
- stolen or deceptively obtained Singpass credentials

These patterns suggest that the first project should focus on detecting suspicious live access before a fraudster can use Singpass as a trusted gateway into downstream abuse.

The most relevant behavioural risks at login are:

- suspicious login approvals
- app-based or QR-based login abuse
- social engineering-led approvals
- remote-control or device-compromise scenarios
- unusual but technically valid authentication journeys

This project is intended to reflect that risk shape.

## Primary problem statement

How can risky login or approval events be detected in real time, and how should the system respond?

The risk engine should support decisions such as:

- allow
- step up
- delay
- block
- allow with enhanced monitoring

The goal is not only to classify fraud. The goal is to support operational decisions under uncertainty.

## Project scope

This first project focuses on the point of live authentication.

The main scored event family is:

- `login_authentication`

The supporting event families are:

- `account_device_lifecycle`

Other event families such as:

- `recovery`
- `consent_data_sharing`
- `digital_signing_authorisation`

remain part of the shared event universe, but they are outside the main scope of version 1 of this project.

In practical terms, this project is designed to reduce the likelihood that risky access is trusted and allowed to proceed. The downstream misuse itself is handled more directly in project 2.

Project 1 therefore focuses on:

- suspicious login context
- unusual authentication journeys
- risky approval behaviour at the point of access

The project does not attempt to fully model downstream misuse after the login has already succeeded.

It is designed to reduce the likelihood that Singpass access can later be misused for:

- downstream fraudulent financial account creation
- attacker control after account sale or relinquishment
- deceptive approval or consent abuse using stolen credentials

## Core fraud scenarios to simulate

The first version should include both legitimate and suspicious login behaviour.

### 1. Normal returning-user login

- known user
- familiar device
- stable region or network context
- normal login timing

### 2. Legitimate travel or device change

- real user
- unusual location or device context
- otherwise normal behaviour

This scenario is important because it creates realistic false-positive pressure.

### 3. Social engineering or malicious approval

- real user identity
- login technically succeeds
- approval pattern or context is unusual
- event sequence suggests possible scam coaching, deceptive QR flow, or malicious approval that may later enable unconsented downstream actions

### 4. Remote-control or device-compromise scenario

- login occurs from a believable or previously linked context
- user identity is valid
- timing, behaviour, or approval sequence is abnormal

This scenario captures cases where the attacker does not need to fully “hack” Singpass in a traditional sense, but instead gains control through device compromise or victim manipulation.

### 5. Repeated attempts before success

- multiple failed or rejected events
- sudden later success
- pattern may indicate probing, coercion, or attack pressure

### 6. Relinquished-account access pattern

- login appears operationally valid
- device and user context may not look obviously malicious at first
- behavioural patterns suggest the account is being operated by someone other than the legitimate holder
- the risk engine should treat the access context itself as suspicious even before downstream misuse is observed

## Data foundation for the project

This project uses the shared minimum viable backend defined in the prerequisite layer.

The main tables used in version 1 are:

- `users`
- `devices`
- `user_devices`
- `services`
- `sessions`
- `events`
- `fraud_labels`

The main analytical table for this project is `events`, using the `login_authentication` category as the primary scored event family.

The supporting context comes from:

- `account_device_lifecycle` events in `events`
- user, device, service, and session context from the other shared tables

## Event types most relevant to project 1

The project should prioritise login and precursor events such as:

- qr_login_request
- qr_login_scan
- qr_login_approval_prompt
- qr_login_approved
- qr_login_rejected
- app_login_request
- app_login_success
- app_login_failure
- face_verification_login_attempt
- face_verification_login_success
- face_verification_login_failure
- device_registered
- device_changed
- app_reinstalled
- passcode_reset
- contact_detail_updated

These events provide enough coverage for realistic version 1 login-risk analysis.

## Abuse patterns this project is designed to intercept

The login-risk engine is not intended to solve every downstream fraud problem directly.

Its role is to intercept risky access before Singpass can be misused in one of the following ways:

### 1. Fraudulent financial account creation

The attacker gains access to Singpass and then uses trusted identity access to create or enable downstream financial accounts.

### 2. Sold or relinquished Singpass account control

The attacker operates a Singpass account that was handed over, sold, or recklessly shared by the legitimate holder.

### 3. Stolen credentials used for deceptive approvals

The attacker relies on stolen credentials, scam coaching, or manipulated approvals to obtain access or trigger actions the victim did not genuinely intend.

These three patterns give the project a more concrete harm model than a generic “account takeover” framing.

## Boundary with project 2

The separation between the two projects is:

- project 1 asks: `Is this login or approval context suspicious enough to intervene now?`
- project 2 asks: `After access is obtained, is the account being misused and how should damage be contained?`

This means project 1 focuses on pre-access or at-access detection, while project 2 focuses on post-login behavioural monitoring.

## Feature engineering direction

The login risk engine should derive features at scoring time from the shared backend tables rather than rely on a single flat dataset.

Initial feature groups:

### 1. User baseline features

- account_age_days
- baseline_login_frequency_band
- baseline_travel_profile
- usual login timing deviation

### 2. Device and trust features

- known_device_flag
- trusted_device_flag
- days_since_last_device_seen
- recent_device_change_flag
- recent_app_reinstall_flag
- device_shared_across_users_flag

### 3. Network and location features

- new_country_flag
- new_region_flag
- new_asn_flag
- impossible_travel_flag
- geo_distance_from_last_login

### 4. Behaviour and sequence features

- failed_or_rejected_events_last_10m
- failed_or_rejected_events_last_24h
- repeated_attempt_then_success_flag
- qr_approval_latency_deviation
- first_time_qr_login_flag
- first_time_service_access_flag
- behaviour_shift_from_user_baseline
- sustained_access_pattern_inconsistency

## Detection approach

The project should use a hybrid detection design.

### 1. Rules layer

Rules provide an interpretable first detection layer.

Examples:

- impossible travel plus successful approval
- repeated failures or rejections followed by success
- device change shortly before login
- first-time service access combined with unusual approval context
- successful access with strong deviation from the user's historical pattern

### 2. ML scoring layer

A supervised tabular model should combine multiple weak signals into a login risk score.

Recommended first model:

- XGBoost or LightGBM

Reason:

- strong baseline for tabular fraud data
- interpretable enough for a portfolio setting
- practical for synthetic event-driven data

### 3. Policy decision layer

The project should separate risk scoring from actioning.

Illustrative mapping:

- low risk -> allow
- medium risk -> step up
- high risk -> block
- uncertain but elevated risk -> allow with monitoring

This makes the project closer to a real fraud-control system than a simple fraud classifier.

## Evaluation approach

The project should evaluate more than overall accuracy.

Relevant views include:

- precision
- recall
- false positive rate
- PR-AUC
- recall at fixed alert rate
- confusion matrix by fraud scenario
- decision distribution by action

Important business framing:

- how many suspicious logins are stopped or stepped up
- how many legitimate logins are inconvenienced
- where false positives concentrate
- whether risky access is interrupted before downstream misuse becomes possible

## Version 1 deliverables

The first version of the project should include:

### 1. Synthetic event generator

Generates shared backend tables with emphasis on login and lifecycle patterns relevant to suspicious access detection.

### 2. Feature engineering pipeline

Builds login-risk features from the shared backend tables.

### 3. Rule-based risk baseline

Applies interpretable fraud rules to login events.

### 4. ML training and evaluation pipeline

Trains a login risk model and evaluates it against the synthetic labels.

### 5. Simple scoring service

Accepts a login-related event payload and returns a risk score and recommended action.

### 6. Reviewer console

Displays flagged login events, triggered signals, and action recommendations.

## Why this project matters even without stored funds in Singpass

Singpass is not primarily a store-of-value target.

The risk is that a compromised, sold, relinquished, or deceptively used Singpass account becomes a trusted gateway into downstream abuse.

That is why preventing suspicious live access still matters:

- it reduces the chance of fraudulent financial account creation
- it reduces the utility of sold or relinquished Singpass accounts
- it interrupts stolen-credential abuse before high-trust identity actions are completed

The second project in the portfolio then takes over the next problem:

- monitoring what happens after access is obtained
- detecting downstream misuse
- containing damage once prevention is imperfect

## Suggested repository structure

```text
singpass-login-risk-engine/
├── data/
├── notebooks/
├── src/
│   ├── simulation/
│   ├── features/
│   ├── rules/
│   ├── models/
│   ├── serving/
│   └── utils/
├── app/
├── outputs/
├── tests/
├── project_plan.md
└── README.md
```

## Conclusion

This project is the login-risk layer of the broader Singpass anti-fraud portfolio.

It is designed to sit directly on top of the shared prerequisite layer rather than introducing a separate dataset or isolated assumptions. That alignment makes the project more realistic, more coherent, and easier to extend later into the second project on post-compromise monitoring.

More importantly, it is now grounded in three concrete Singpass misuse patterns identified through recent official materials:

- fraudulent financial account creation
- sale or relinquishment of Singpass accounts or credentials
- stolen or deceptively used Singpass credentials
