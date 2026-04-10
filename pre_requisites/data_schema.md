# Shared Data Schema

Last updated: 4 April 2026

## Purpose

This document defines the minimum viable shared data schema for the Singpass anti-fraud portfolio.

It is designed to support both planned project directions:

- minimising compromise of accounts at the point of live login
- minimising damage after compromise through active monitoring

The purpose of this schema is not to reproduce the internal design of the real Singpass platform. It is a project design artifact intended to show how a realistic fraud data environment could be structured before any rules, models, or dashboards are built on top of it.

## Design rationale

The portfolio is built on one shared synthetic data universe rather than two separate project datasets.

This means:

- the same users, devices, services, and sessions exist across both projects
- project 1 uses the login-centric slice of the data
- project 2 uses the post-authentication and post-compromise slice of the same data

This approach is closer to how fraud systems are developed in practice. It also creates a more coherent portfolio because both projects operate on the same underlying environment.

## Minimum viable schema

The first version of the schema contains seven core tables:

1. users
2. devices
3. user_devices
4. services
5. sessions
6. events
7. fraud_labels

This is the smallest structure that can still support:

- authentication and approval event simulation
- trusted-device and service context
- sequence analysis before and after login
- fraud scenario evaluation for both projects

## 1. users

Purpose:

- represents the account holder in the synthetic Singpass-like environment
- stores stable user-level context for behavioural analysis

Minimum fields:

- user_id
- user_created_at
- account_status
- account_age_days
- age_band
- primary_region
- baseline_login_frequency_band
- baseline_travel_profile

Why it is included:

- both projects need a user-level anchor
- user baselines help later anomaly detection feel more realistic

## 2. devices

Purpose:

- represents mobile devices or app-linked endpoints used by the account holder
- stores device-level context relevant to fraud analysis

Minimum fields:

- device_id
- device_first_seen_at
- os_type
- os_version
- app_version
- biometric_capable_flag
- device_status
- rooted_or_compromised_flag
- emulator_flag

Why it is included:

- device context is important in both login risk and post-compromise monitoring

## 3. user_devices

Purpose:

- maps users to devices over time
- captures trusted-device and linkage context

Minimum fields:

- user_device_id
- user_id
- device_id
- linked_at
- unlinked_at
- is_primary_device_flag
- trust_status
- last_seen_at

Why it is included:

- it separates the device itself from the relationship between a user and a device
- it supports trusted-device logic and potential device-sharing analysis

## 4. services

Purpose:

- represents the service being accessed through the Singpass-like ecosystem

Minimum fields:

- service_id
- service_name
- sector_type
- risk_tier
- supports_myinfo_flag
- supports_signing_flag

Why it is included:

- fraud risk depends partly on what type of service the user is accessing
- both projects benefit from service-level context

## 5. sessions

Purpose:

- groups related events within one login or authenticated journey

Minimum fields:

- session_id
- user_id
- device_id
- service_id
- session_start_at
- session_end_at
- session_status
- login_method
- authenticated_flag

Why it is included:

- project 1 needs login-level grouping
- project 2 needs post-authentication session monitoring

## 6. events

Purpose:

- acts as the master event log across all categories defined in the Singpass event taxonomy

Minimum fields:

- event_id
- event_timestamp
- event_category
- event_type
- user_id
- device_id
- service_id
- session_id
- ip_address
- asn
- country
- region
- channel
- event_result
- approval_latency_seconds
- event_metadata_json

Expected event categories:

- login_authentication
- digital_signing_authorisation
- consent_data_sharing
- recovery
- account_device_lifecycle

Why it is included:

- it is the central table in the shared schema
- it allows both projects to work from the same event universe
- it supports sequence analysis across login, recovery, consent, signing, and lifecycle activity

Scope note:

- network fields are embedded directly into `events` for simplicity in version 1
- if the project expands later, those fields can be normalised into a dedicated network table

## 7. fraud_labels

Purpose:

- stores synthetic ground-truth labels for evaluation

Minimum fields:

- label_id
- event_id
- user_id
- label_timestamp
- is_fraud_flag
- fraud_scenario
- fraud_stage
- downstream_damage_flag

Why it is included:

- both projects need evaluation labels
- keeping labels separate from raw event data is closer to real fraud workflows, where labels often arrive later than the original event

## Why this schema is sufficient for the portfolio

Although the schema is deliberately lean, it is sufficient for both projects.

For the login-risk project, it supports:

- live authentication and approval events
- recovery signals occurring before login
- device and network context
- session-level grouping
- event-level fraud evaluation

For the post-compromise monitoring project, it supports:

- post-authentication event sequences
- consent, signing, and lifecycle activity after login
- suspicious chains of behaviour across a user, device, or service
- downstream damage labelling

## What is intentionally deferred

The following tables are intentionally deferred from version 1:

- journeys
- networks
- login_attempts
- recovery_cases
- consent_actions
- signing_actions
- device_lifecycle_events
- risk_decisions
- investigations

These are all valid extensions, but they are not required for the minimum viable shared design. Most of their information can be represented initially through `events`, `sessions`, and `fraud_labels`.

## Conclusion

This schema provides a realistic minimum backend structure for a Singpass-like anti-fraud environment.

It is deliberately compact, but it still preserves the most important design principle for the portfolio:

both projects should be built on the same underlying data environment, with project-specific analysis layered on top later.
