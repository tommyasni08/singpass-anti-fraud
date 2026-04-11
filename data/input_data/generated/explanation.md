# Generated Data Explanation

Last updated: 11 April 2026

## Purpose

This document explains the current generated version of the shared synthetic dataset.

It covers:

- the current dataset shape
- the calibration changes that were made
- why `fraud_labels.csv` has fewer rows than `events.csv`
- one concrete walkthrough example for each injected scenario

This file is meant to make the raw generated data easier to inspect before feature engineering and model development.

## Generated dataset summary

Current row counts:

- `users.csv`: 5,000
- `devices.csv`: 6,425
- `user_devices.csv`: 6,425
- `services.csv`: 12
- `sessions.csv`: 40,032
- `events.csv`: 155,314
- `fraud_labels.csv`: 78,866
- `session_context.csv`: 40,032

Scenario counts:

- `normal_returning_login_and_normal_usage`: 26,096
- `legitimate_travel_or_device_change_login`: 3,956
- `social_engineering_or_malicious_approval`: 2,436
- `legitimate_first_time_or_infrequent_service_usage`: 2,025
- `remote_control_or_device_compromise_access`: 1,606
- `relinquished_account_access_and_operation`: 1,556
- `repeated_attempts_before_success`: 1,198
- `suspicious_downstream_misuse_after_successful_access`: 1,159

Event category counts:

- `login_authentication`: 109,362
- `service_usage`: 33,683
- `account_device_lifecycle`: 7,118
- `digital_signing_authorisation`: 2,582
- `consent_data_sharing`: 2,569

Fraud label summary:

- login-stage non-fraud labels: 35,147
- login-stage fraud labels: 4,885
- post-login-stage non-fraud labels: 32,077
- post-login-stage fraud labels: 6,757

## What changed during calibration

### 1. Login-stage labels were restricted to access-time visibility

Login-stage labels now reflect only what is observable at the moment of authentication.

This matters for:

- `social_engineering_or_malicious_approval`
- `relinquished_account_access_and_operation`

Both scenarios can now appear in two forms:

- login already suspicious -> login-stage fraud and post-login-stage fraud
- login not clearly suspicious -> login-stage non-fraud and post-login-stage fraud

### 2. Legitimate post-login continuations were expanded

Earlier versions had too many sessions with login activity only and too few benign post-login records.

To make the behavioural baseline more realistic, legitimate sessions now commonly continue into ordinary post-login activity through the `service_usage` event family.

Typical benign post-login events now include:

- `service_access_view`
- `dashboard_view`
- `profile_view`
- `history_view`

This change means most successful logins now have a modeled continuation after authentication, which is closer to real product usage and gives project 2 a more realistic non-fraud baseline.

### 3. Why `fraud_labels.csv` has fewer rows than `events.csv`

`events.csv` contains the full event log.

`fraud_labels.csv` only labels the target events used for fraud evaluation:

- decisive login-stage events such as `app_login_success` or `qr_login_approved`
- decisive post-login events such as `service_access_view`, `consent_granted`, `sign_completed`, or similar downstream targets

Precursor events are intentionally not all labeled. Examples:

- `app_login_request`
- `qr_login_request`
- `qr_login_approval_prompt`
- `contact_detail_updated`

So the design is:

- `events.csv` = full behavioral log
- `fraud_labels.csv` = scoring targets extracted from that log

## Scenario walkthroughs

The examples below use actual generated records from the current dataset.

## 1. Normal returning-user login and normal usage

Example:

- `user_id`: `U000001`
- `device_id`: `D000001`
- `service_id`: `S0010`
- `session_id`: `SE000001`

Events:

- `E00000001`: `login_authentication` -> `app_login_request`
- `E00000002`: `login_authentication` -> `app_login_success`
- `E00000003`: `service_usage` -> `history_view`

Fraud labels:

- `L000001`
  - stage: `login_stage`
  - fraud: `False`
  - scenario: `normal_returning_login_and_normal_usage`
- `L000002`
  - stage: `post_login_stage`
  - fraud: `False`
  - scenario: `normal_returning_login_and_normal_usage`

Interpretation:

- this is the main baseline case
- the user logs in successfully
- the session then continues into a benign downstream action
- both the login and the downstream activity remain non-fraud

## 2. Legitimate travel or device-change login

Example:

- `user_id`: `U000002`
- `device_id`: `D000004`
- `service_id`: `S0004`
- `session_id`: `SE000010`

Events:

- `E00000032`: `login_authentication` -> `qr_login_request`
- `E00000033`: `login_authentication` -> `qr_login_approval_prompt`
- `E00000034`: `login_authentication` -> `qr_login_approved`
- `E00000035`: `account_device_lifecycle` -> `contact_detail_updated`
- `E00000036`: `service_usage` -> `service_access_view`

Fraud labels:

- `L000019`
  - stage: `login_stage`
  - fraud: `False`
  - scenario: `legitimate_travel_or_device_change_login`
- `L000020`
  - stage: `post_login_stage`
  - fraud: `False`
  - scenario: `legitimate_travel_or_device_change_login`

Interpretation:

- the login context is unusual enough to create false-positive pressure for project 1
- the session still resolves into legitimate downstream usage
- this is an important non-fraud example for both projects

## 3. Legitimate first-time or infrequent service usage

Example:

- `user_id`: `U000001`
- `device_id`: `D000001`
- `service_id`: `S0010`
- `session_id`: `SE000002`

Events:

- `E00000004`: `login_authentication` -> `app_login_request`
- `E00000005`: `login_authentication` -> `app_login_success`
- `E00000006`: `service_usage` -> `profile_view`

Fraud labels:

- `L000003`
  - stage: `login_stage`
  - fraud: `False`
  - scenario: `legitimate_first_time_or_infrequent_service_usage`
- `L000004`
  - stage: `post_login_stage`
  - fraud: `False`
  - scenario: `legitimate_first_time_or_infrequent_service_usage`

Interpretation:

- the login itself is clean
- the user performs a less common but still legitimate downstream action
- this scenario is one of the main non-fraud post-login baselines for project 2

## 4. Social engineering or malicious approval

This scenario exists in two forms in the generated data.

### 4A. Social engineering with suspicious login context

Example:

- `user_id`: `U000001`
- `device_id`: `D000001`
- `service_id`: `S0006`
- `session_id`: `SE000003`

Events:

- `E00000007`: `login_authentication` -> `qr_login_request`
- `E00000008`: `login_authentication` -> `qr_login_approval_prompt`
- `E00000009`: `login_authentication` -> `qr_login_approved`
- `E00000010`: `consent_data_sharing` -> `consent_request_presented`

Fraud labels:

- `L000005`
  - stage: `login_stage`
  - fraud: `True`
  - scenario: `social_engineering_or_malicious_approval`
- `L000006`
  - stage: `post_login_stage`
  - fraud: `True`
  - scenario: `social_engineering_or_malicious_approval`

Interpretation:

- the access context is already suspicious enough to flag at login time
- downstream misuse also appears after access is obtained
- this is a case where both project 1 and project 2 should react

### 4B. Social engineering with non-obvious login context

Example:

- `user_id`: `U000002`
- `device_id`: `D000002`
- `service_id`: `S0010`
- `session_id`: `SE000008`

Events:

- `E00000024`: `login_authentication` -> `app_login_request`
- `E00000025`: `login_authentication` -> `app_login_success`
- `E00000026`: `digital_signing_authorisation` -> `sign_approved`

Fraud labels:

- `L000015`
  - stage: `login_stage`
  - fraud: `False`
  - scenario: `social_engineering_or_malicious_approval`
- `L000016`
  - stage: `post_login_stage`
  - fraud: `True`
  - scenario: `social_engineering_or_malicious_approval`

Interpretation:

- the login itself is not clearly suspicious enough to block or step up
- the misuse only becomes visible after authentication
- this is the kind of case project 2 is meant to catch

## 5. Remote-control or device-compromise access

Example:

- `user_id`: `U000004`
- `device_id`: `D000006`
- `service_id`: `S0010`
- `session_id`: `SE000027`

Events:

- `E00000098`: `login_authentication` -> `qr_login_request`
- `E00000099`: `login_authentication` -> `qr_login_approval_prompt`
- `E00000100`: `login_authentication` -> `qr_login_approved`
- `E00000101`: `account_device_lifecycle` -> `contact_detail_updated`
- `E00000102`: `service_usage` -> `dashboard_view`

Fraud labels:

- `L000053`
  - stage: `login_stage`
  - fraud: `True`
  - scenario: `remote_control_or_device_compromise_access`
- `L000054`
  - stage: `post_login_stage`
  - fraud: `True`
  - scenario: `remote_control_or_device_compromise_access`

Interpretation:

- the login itself is suspicious and should be intercepted by project 1
- the downstream continuation is also treated as misuse
- this scenario represents access that is already compromised at the point of authentication

## 6. Repeated attempts before success

Example:

- `user_id`: `U000004`
- `device_id`: `D000006`
- `service_id`: `S0002`
- `session_id`: `SE000028`

Events:

- `E00000103`: `login_authentication` -> `qr_login_request`
- `E00000104`: `login_authentication` -> `qr_login_rejected`
- `E00000105`: `login_authentication` -> `qr_login_request`
- `E00000106`: `login_authentication` -> `qr_login_rejected`
- `E00000107`: `login_authentication` -> `qr_login_request`
- `E00000108`: `login_authentication` -> `qr_login_rejected`
- `E00000109`: `login_authentication` -> `qr_login_request`
- `E00000110`: `login_authentication` -> `qr_login_approval_prompt`
- `E00000111`: `login_authentication` -> `qr_login_rejected`

Fraud labels:

- `L000055`
  - stage: `login_stage`
  - fraud: `True`
  - scenario: `repeated_attempts_before_success`

Interpretation:

- this is a login-stage-only fraud case
- the suspiciousness comes from the repeated failed pattern itself
- there is no successful authenticated continuation in this example

## 7. Relinquished-account access and operation

This scenario also exists in two forms in the generated data.

### 7A. Relinquished-account access with suspicious login context

Example:

- `user_id`: `U000008`
- `device_id`: `D000011`
- `service_id`: `S0010`
- `session_id`: `SE000063`

Events:

- `E00000240`: `login_authentication` -> `app_login_request`
- `E00000241`: `login_authentication` -> `app_login_success`
- `E00000242`: `account_device_lifecycle` -> `contact_detail_updated`
- `E00000243`: `consent_data_sharing` -> `consent_granted`

Fraud labels:

- `L000124`
  - stage: `login_stage`
  - fraud: `True`
  - scenario: `relinquished_account_access_and_operation`
- `L000125`
  - stage: `post_login_stage`
  - fraud: `True`
  - scenario: `relinquished_account_access_and_operation`

Interpretation:

- the access itself is suspicious enough to score as fraud
- downstream activity confirms harmful use of the account
- this is another case where both projects should respond

### 7B. Relinquished-account access with non-obvious login context

Example:

- `user_id`: `U000002`
- `device_id`: `D000002`
- `service_id`: `S0012`
- `session_id`: `SE000009`

Events:

- `E00000027`: `login_authentication` -> `qr_login_request`
- `E00000028`: `login_authentication` -> `qr_login_approval_prompt`
- `E00000029`: `login_authentication` -> `qr_login_approved`
- `E00000030`: `account_device_lifecycle` -> `contact_detail_updated`
- `E00000031`: `digital_signing_authorisation` -> `sign_completed`

Fraud labels:

- `L000017`
  - stage: `login_stage`
  - fraud: `False`
  - scenario: `relinquished_account_access_and_operation`
- `L000018`
  - stage: `post_login_stage`
  - fraud: `True`
  - scenario: `relinquished_account_access_and_operation`

Interpretation:

- the login looks plausible at authentication time
- misuse becomes visible only after the account is already in use
- this is the kind of case where project 2 adds value beyond project 1

## 8. Suspicious downstream misuse after successful access

Example:

- `user_id`: `U000007`
- `device_id`: `D000010`
- `service_id`: `S0008`
- `session_id`: `SE000048`

Events:

- `E00000183`: `login_authentication` -> `qr_login_request`
- `E00000184`: `login_authentication` -> `qr_login_approval_prompt`
- `E00000185`: `login_authentication` -> `qr_login_approved`
- `E00000186`: `consent_data_sharing` -> `myinfo_data_access_completed`

Fraud labels:

- `L000094`
  - stage: `login_stage`
  - fraud: `False`
  - scenario: `suspicious_downstream_misuse_after_successful_access`
- `L000095`
  - stage: `post_login_stage`
  - fraud: `True`
  - scenario: `suspicious_downstream_misuse_after_successful_access`

Interpretation:

- the login is intentionally treated as non-fraud
- the misuse only appears in the downstream action
- this is the clearest project 2 scenario in the current dataset

## Final note on stage-specific labels

The same scenario name can produce different login-stage outcomes.

This is intentional.

The login-stage label answers:

- was the session already suspicious enough at authentication time?

The post-login-stage label answers:

- after access was obtained, did the session continue into misuse or remain benign?

That distinction is necessary because the two projects are solving different problems on top of the same shared dataset:

- project 1: suspicious live login detection
- project 2: post-login misuse monitoring and damage containment
