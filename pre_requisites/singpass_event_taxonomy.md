# Singpass Event Taxonomy

Last updated: 4 April 2026

## Purpose

This document defines a working event taxonomy for a Singpass-like anti-fraud dataset.

It is prepared before designing the shared data schema and backend table structure for the portfolio projects. The purpose is to map the major categories of user and system events involved in the Singpass ecosystem so that the later project design is grounded in a realistic operating context.

This taxonomy is intended to support both planned project directions:

- minimising compromise of accounts at the point of live login
- minimising damage after compromise through active monitoring

## Why an event taxonomy is needed first

For a fraud project to be relevant, it must be built on the right event universe.

Singpass is not a generic consumer app. It is a high-trust digital identity system that includes authentication, consent-based data sharing, digital signing, recovery flows, and device-linked trust signals. Because of that, the project should not begin with rules or models first. It should begin by identifying the core event families that define how users interact with the system.

This taxonomy is meant to be that foundation.

## Design decisions used in this taxonomy

The following decisions guide this version:

- Username-and-password login is excluded from the primary taxonomy because current official Singpass Login / Myinfo documentation frames new integrations around QR-based login rather than password / SMS OTP login.
- Recovery is framed as account access recovery rather than password reset.
- Consent is treated as a full event family, not just a single positive outcome.
- Digital signing is treated as its own category because it is a core Singpass capability with distinct fraud implications.
- Account and device lifecycle events are included because they provide important trust context for both login risk and post-compromise monitoring.

## Event categories

### 1. Login / Authentication

This category covers authentication attempts into services through a Singpass-like flow.

Representative event types:

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

Why this category matters:

- it is the primary event family for the first project
- it captures the live point where suspicious access may be allowed, stepped up, delayed, or blocked
- it reflects the app-based and approval-based nature of the Singpass authentication experience

### 2. Digital Signing / Authorisation

This category covers high-trust approval and signing events performed through the Singpass ecosystem.

Representative event types:

- sign_request_initiated
- sign_portal_accessed
- sign_document_viewed
- sign_reference_code_verified
- sign_approval_prompt
- sign_approved
- sign_rejected
- sign_completed
- sign_cancelled

Why this category matters:

- digital signing is part of the Singpass capability surface, not only a downstream application action
- it introduces high-consequence approval events that may be technically valid but risky in intent
- it is especially relevant for modelling abuse beyond ordinary login success or failure

### 3. Consent / Data Sharing

This category covers user consent and the resulting data-sharing flow, such as Myinfo-related access.

Representative event types:

- consent_request_presented
- consent_scope_reviewed
- consent_granted
- consent_rejected
- consent_cancelled
- consent_timeout
- myinfo_data_access_completed

Why this category matters:

- in a Singpass-like system, fraud risk can sit in manipulated or misunderstood approvals, not only in account takeover
- modelling both successful and unsuccessful consent outcomes helps represent realistic user journeys

### 4. Recovery

This category covers the process of regaining trusted access or re-establishing identity assurance when a user cannot proceed normally.

Representative event types:

- account_recovery_request
- otp_challenge_sent
- otp_success
- otp_failure
- face_verification_recovery_attempt
- face_verification_recovery_success
- face_verification_recovery_failure
- pin_mailer_requested
- counter_recovery_visit
- counter_recovery_completed

Why this category matters:

- recovery events are often powerful fraud signals because they can appear shortly before suspicious authentication or approval activity
- in a Singpass-like system, recovery should be understood more broadly than password reset alone

### 5. Account / Device Lifecycle

This category covers events that change trust state or influence future authentication risk.

Representative event types:

- singpass_app_registered
- device_registered
- device_deregistered
- device_changed
- app_reinstalled
- passcode_reset
- biometric_enabled
- biometric_disabled
- contact_detail_updated

Why this category matters:

- these events often provide important context even when they are not the primary event being scored
- they can be useful for both login-risk detection and post-compromise behavioural monitoring

## How this taxonomy supports the two planned projects

For the first project, the main scored event family will be `Login / Authentication`. The other categories provide surrounding context, precursor signals, or linked high-trust actions that help make login-risk scoring more realistic.

For the second project, the event universe can expand naturally into `Digital Signing / Authorisation`, `Consent / Data Sharing`, `Recovery`, and `Account / Device Lifecycle`, which are all relevant for post-compromise monitoring and damage containment.

This shared taxonomy supports a coherent portfolio design where both projects operate on the same Singpass-like environment rather than on two unrelated synthetic systems.

## Scope note

This taxonomy is not meant to represent the full internal event model of the real Singpass platform. It is a project design artifact meant to approximate the most relevant event families for anti-fraud analysis in a Singpass-like setting.

The next step after this taxonomy is to define the shared data schema and backend table design that can support both projects.

## Sources consulted

These sources were reviewed on 4 April 2026.

- GovTech Singpass overview: https://www.tech.gov.sg/products-and-services/singpass/
- Singpass app overview: https://app.singpass.gov.sg/
- Singpass Login documentation: https://docs.developer.singpass.gov.sg/docs/products/singpass-login
- Singpass Login FAQ: https://docs.developer.singpass.gov.sg/docs/products/singpass-login/faq
- Myinfo technical documentation: https://docs.developer.singpass.gov.sg/docs/legacy-myinfo-v3-v4/technical-specifications/myinfo-v4
- Sign with Singpass overview: https://docs.sign.singpass.gov.sg/
- Sign with Singpass user flow: https://docs.sign.singpass.gov.sg/for-users/how-to-sign
