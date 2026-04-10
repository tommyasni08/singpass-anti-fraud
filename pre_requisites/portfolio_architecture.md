# Portfolio Architecture

Last updated: 8 April 2026

## Purpose

This document explains how the Singpass anti-fraud portfolio is structured end to end.

Its main purpose is to clarify:

- what the shared input is
- how project 1 and project 2 differ
- what each project is expected to output
- what the deliverables look like at each stage

This is a portfolio-level architecture document, not a system implementation specification.

## Portfolio objective

The portfolio is built around two complementary anti-fraud objectives:

1. minimise compromise at the point of live login
2. minimise damage after compromise through active monitoring

Together, the two projects model a realistic fraud-control system:

- first detect suspicious access before it is trusted
- then monitor what happens after access is obtained and contain damage if prevention was imperfect

## Shared foundation

Both projects are built on the same prerequisite layer.

That shared layer includes:

- product understanding: `initial_research`
- event universe: `singpass_event_taxonomy`
- shared schema: `data_schema`
- backend design: `backend_table_design`
- shared scenario universe: `shared_simulation_scenarios`

This means the portfolio uses one synthetic environment, not two unrelated datasets.

## Shared input

The common input to both projects is a shared synthetic backend made up of:

- `users`
- `devices`
- `user_devices`
- `services`
- `sessions`
- `events`
- `fraud_labels`

This backend represents the raw operating environment.

In practical terms, the shared input is:

- synthetic user and device populations
- synthetic login and post-login event streams
- session history
- service-level context
- fraud scenario labels for evaluation

## High-level data flow

The portfolio can be understood as a staged pipeline:

1. shared prerequisite design
2. shared synthetic data generation
3. project 1 analysis on the login slice
4. project 2 analysis on the post-login slice
5. evaluation and reviewer-facing outputs

## Stage 1: Shared prerequisite design

Input:

- Singpass product research
- event taxonomy
- shared schema design
- backend table design
- shared abuse and scenario definitions

Output:

- project design documents
- a shared conceptual data model

Deliverable format:

- markdown design documents

This stage exists so that the later work is grounded in a realistic problem frame rather than ad hoc fraud assumptions.

## Stage 2: Shared synthetic data generation

Input:

- shared schema
- backend table design
- shared scenario definitions

Output:

- synthetic backend tables
- labelled events and sessions

Deliverable format:

- generated CSV, Parquet, or local data files
- data-generation scripts
- optional notebooks for inspection

This is the common data layer both projects rely on.

## Stage 3: Project 1

Project:

- `singpass-login-risk-engine`

Primary question:

- `Should this login or approval be trusted right now?`

Input slice:

- login-related events
- device context
- session context
- account and device lifecycle context

Main analytical unit:

- login event
- approval event
- login session at the point of access

Primary output:

- login-level risk score
- recommended action such as:
  - allow
  - step_up
  - delay
  - block
  - allow_with_monitoring

Secondary output:

- explanation of triggered signals
- rule hits
- model score drivers

Deliverable format:

- simulation pipeline for login-related data
- feature engineering pipeline
- rule engine
- baseline ML model
- scoring service or script
- reviewer console or dashboard for flagged login events

In practical terms, project 1 delivers:

- a real-time login risk engine

## Stage 4: Project 2

Project:

- `singpass-post-compromise-monitoring`

Primary question:

- `Now that access exists, is the account being misused and how should damage be contained?`

Input slice:

- authenticated sessions
- post-login events
- downstream service usage
- consent, signing, and lifecycle behaviour
- user and device historical context

Main analytical unit:

- session
- sequence of events
- account-level behaviour over time

Primary output:

- session-level or account-level misuse risk score
- suspicious case or monitoring flag
- recommended containment action such as:
  - monitor
  - escalate
  - restrict
  - hold_sensitive_action
  - investigate

Secondary output:

- explanation of suspicious behavioural sequence
- highlighted downstream risk indicators

Deliverable format:

- post-login simulation layer
- session or sequence feature pipeline
- rule-based monitoring logic
- behavioural scoring model
- monitoring dashboard or case-review console

In practical terms, project 2 delivers:

- a post-login misuse monitoring engine

## Relationship between the two projects

The two projects are connected, but they do not do the same job.

Project 1:

- focuses on prevention at access time
- decides whether a login or approval should be trusted

Project 2:

- focuses on containment after access time
- decides whether downstream behaviour suggests misuse and whether intervention is needed

The clean mental model is:

- project 1 = `Is this access suspicious?`
- project 2 = `Is this trusted identity now being misused?`

## Deliverables by layer

### 1. Prerequisite deliverables

Format:

- markdown documents

Examples:

- research note
- event taxonomy
- shared schema
- backend table design
- shared scenario definitions

### 2. Data deliverables

Format:

- generated data files
- simulation code
- optional exploratory notebooks

Examples:

- synthetic event tables
- labelled fraud cases
- sample sessions

### 3. Project 1 deliverables

Format:

- code pipelines
- model artifacts
- rule logic
- scoring outputs
- reviewer-facing interface

Examples:

- login risk score output
- recommended action output
- login-review dashboard

### 4. Project 2 deliverables

Format:

- monitoring pipelines
- model artifacts
- rule logic
- case or alert outputs
- reviewer-facing interface

Examples:

- suspicious session output
- containment recommendation
- post-login monitoring dashboard

## End-to-end example

A simplified end-to-end flow would look like this:

1. Shared simulation generates a user, device, service, session, and event sequence.
2. Project 1 consumes the login-related events and decides whether the access should be trusted.
3. If the session proceeds, project 2 consumes the post-login events and decides whether the behaviour indicates misuse.
4. Both projects are evaluated against the shared fraud labels.

This makes the portfolio feel like one connected anti-fraud system rather than two disconnected demos.

## Conclusion

The portfolio architecture is intentionally simple:

- one shared synthetic backend
- one login-risk project
- one post-compromise monitoring project

The value of this structure is that it mirrors a realistic fraud workflow:

- prevent suspicious access where possible
- monitor and contain harm when prevention is incomplete
