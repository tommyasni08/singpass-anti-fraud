# Shared Simulation Scenarios

Last updated: 10 April 2026

## Purpose

This document defines the shared scenario universe for the Singpass anti-fraud portfolio.

Its purpose is to ensure that both projects operate on the same synthetic environment:

- project 1: minimise compromise at the point of live login
- project 2: minimise damage after compromise through active monitoring

This document does not describe implementation details yet. It defines the behavioural situations that the shared dataset should represent before any rules, models, or dashboards are built.

## Why this document is shared

The portfolio uses one shared synthetic backend, not two unrelated datasets.

That means the scenarios must also be defined from one shared fraud universe first.

Project 1 and project 2 then consume different slices of the same environment:

- project 1 focuses on suspicious access at the login stage
- project 2 focuses on misuse after access is already obtained

## Main abuse patterns covered

The shared scenario universe is built around three main Singpass abuse patterns identified through the research:

### 1. Fraudulent account creation in downstream financial services

The attacker obtains Singpass access and uses trusted identity access for downstream financial abuse.

### 2. Sale or relinquishment of Singpass accounts or credentials

The attacker operates a Singpass account that was handed over, sold, or recklessly shared by the legitimate holder.

### 3. Stolen or deceptively obtained Singpass credentials

The attacker uses stolen credentials or manipulated approvals to obtain access or trigger actions the victim did not genuinely intend.

## Design principle

The simulation should contain both:

- legitimate behaviour that creates realistic false-positive pressure
- suspicious behaviour that reflects the three main abuse patterns

The objective is not only to create obviously fraudulent records. The objective is to create believable user journeys where:

- project 1 can evaluate suspicious access
- project 2 can evaluate suspicious usage after access

## Scenario structure

Each shared scenario should support one or both of the following stages:

### Login stage

Used mainly by project 1.

This stage asks:

- does the login or approval context itself look suspicious?

### Post-login stage

Used mainly by project 2.

This stage asks:

- once access is obtained, does the behaviour suggest misuse?

Some scenarios only matter at one stage. Others span both.

## Shared scenario set

The shared synthetic environment should include eight scenarios.

### Scenario 1: Normal returning-user login and normal usage

Type:

- legitimate

Description:

- a real user logs in under expected conditions
- the device is familiar
- network and timing look ordinary
- service usage after login is consistent with normal behaviour

Project relevance:

- project 1: yes
- project 2: yes

Why this scenario exists:

- provides the normal baseline for both login behaviour and post-login usage

### Scenario 2: Legitimate travel or device-change login

Type:

- legitimate but unusual

Description:

- a real user logs in while traveling, switching device, or using an unusual network context
- the login looks unusual on some dimensions but remains legitimate
- post-login behaviour is still coherent and normal

Project relevance:

- project 1: yes
- project 2: optionally yes as a low-risk normal continuation

Why this scenario exists:

- creates realistic false-positive pressure
- prevents project 1 from treating every unfamiliar context as fraud

### Scenario 3: Legitimate first-time or infrequent service usage

Type:

- legitimate but unusual

Description:

- the user successfully logs in
- they access a service they rarely or never use
- the behaviour is unusual, but still coherent and legitimate

Project relevance:

- project 1: limited
- project 2: yes

Why this scenario exists:

- prevents project 2 from overfitting on novelty alone

### Scenario 4: Social engineering or malicious approval

Type:

- fraud

Main abuse pattern:

- stolen or deceptively obtained credentials

Description:

- the user identity is real
- authentication succeeds
- the approval is obtained through scam coaching, deceptive QR flow, or user manipulation
- the access looks technically valid but contextually suspicious

Project relevance:

- project 1: yes
- project 2: yes if misuse continues after login

Why this scenario matters:

- it captures a core Singpass-specific fraud problem where user intent is compromised rather than identity existence

### Scenario 5: Remote-control or device-compromise access

Type:

- fraud

Main abuse pattern:

- stolen or deceptively obtained credentials

Description:

- the attacker gains access through device compromise, remote-control abuse, or manipulated control of a believable device context
- the login may come from a known device or plausible environment
- behaviour at login and after login is abnormal relative to the legitimate user's baseline

Project relevance:

- project 1: yes
- project 2: yes

Why this scenario matters:

- it captures cases where classical “new device = bad” logic is insufficient

### Scenario 6: Repeated attempts before success

Type:

- fraud

Main abuse pattern:

- stolen or deceptively obtained credentials

Description:

- multiple failed, rejected, or abandoned attempts occur before a successful login
- the eventual success may follow pressure, probing, or iterative attacker experimentation

Project relevance:

- project 1: yes
- project 2: optionally yes if the session continues into suspicious usage

Why this scenario matters:

- it introduces temporal attack behaviour and attempt-history signals

### Scenario 7: Relinquished-account access and operation

Type:

- fraud

Main abuse patterns:

- sale or relinquishment of Singpass accounts or credentials
- fraudulent account creation in downstream financial services

Description:

- the attacker operates a Singpass account that has been handed over, sold, or recklessly shared
- the login may not look obviously malicious in a technical sense
- stronger evidence may emerge over time through sustained behavioural inconsistency

Project relevance:

- project 1: yes, as suspicious access context
- project 2: yes, as sustained misuse over multiple sessions

Why this scenario matters:

- it is one of the most important abuse patterns highlighted in recent SPF materials

### Scenario 8: Suspicious downstream misuse after successful access

Type:

- fraud

Main abuse patterns:

- fraudulent account creation in downstream financial services
- stolen or deceptively obtained credentials
- sale or relinquishment of Singpass accounts or credentials

Description:

- access is obtained
- post-login behaviour suggests suspicious downstream activity such as unusual consent flows, unusual signing flows, unfamiliar service usage, or high-risk sequence patterns
- the strongest signal appears after authentication rather than during it

Project relevance:

- project 1: no, except as future downstream outcome
- project 2: yes

Why this scenario matters:

- it represents the core motivation for the second project

## Mapping scenarios to projects

| Scenario | Legit / Fraud | Project 1 | Project 2 |
| --- | --- | --- | --- |
| Normal returning-user login and normal usage | Legitimate | Yes | Yes |
| Legitimate travel or device-change login | Legitimate | Yes | Optional |
| Legitimate first-time or infrequent service usage | Legitimate | Limited | Yes |
| Social engineering or malicious approval | Fraud | Yes | Yes |
| Remote-control or device-compromise access | Fraud | Yes | Yes |
| Repeated attempts before success | Fraud | Yes | Optional |
| Relinquished-account access and operation | Fraud | Yes | Yes |
| Suspicious downstream misuse after successful access | Fraud | No | Yes |

## Event families involved

Across the shared scenario universe, the main event families are:

- `login_authentication`
- `account_device_lifecycle`
- `consent_data_sharing`
- `digital_signing_authorisation`

Selected `recovery` events may be added later if needed, but they are not required for version 1.

## Event emphasis by project

### Project 1 emphasis

The most relevant event families are:

- `login_authentication`
- `account_device_lifecycle`

Project 1 mainly evaluates:

- login requests
- login approvals
- login outcomes
- device or account-state changes near the point of access

### Project 2 emphasis

The most relevant event families are:

- `login_authentication`, as session entry
- `consent_data_sharing`
- `digital_signing_authorisation`
- `account_device_lifecycle`

Project 2 mainly evaluates:

- post-login service usage
- consent actions
- signing actions
- risky event sequences
- sustained behavioural inconsistency across sessions

## What should be labelled as fraud

The exact label design can be finalized later, but the shared logic should be:

- legitimate scenarios remain non-fraud
- fraud scenarios may generate both login-stage and post-login-stage labels depending on the scenario

A practical starting point is:

- project 1 consumes labels attached to the suspicious login or approval event
- project 2 consumes labels attached to the suspicious session or downstream event sequence

This means one shared scenario can create different analytical labels at different stages.

## Label design for version 1

The shared synthetic dataset should support both event-level and session-level labelling.

### Event-level labels

Event-level labels are primarily used by project 1.

Recommended logic:

- label the decisive login or approval event when the suspicious behaviour is visible at access time
- keep ordinary precursor events unlabelled or non-fraud unless they are explicitly part of the scored event set

Examples:

- `qr_login_approved` in a malicious approval scenario -> fraud
- `app_login_success` after repeated suspicious attempts -> fraud
- `app_login_success` in a normal returning-user login -> non-fraud

### Session-level labels

Session-level labels are primarily used by project 2.

Recommended logic:

- label the session as fraud when the post-login sequence indicates misuse
- this allows downstream behaviour to be evaluated even if the login event itself was not obviously fraudulent

Examples:

- a session containing unusual consent and signing activity after access -> fraud
- a session with normal service usage after a legitimate login -> non-fraud

### Cross-stage label logic

Some scenarios should create fraud labels at both stages.

Examples:

- `social engineering or malicious approval`
  - login-stage label: yes
  - post-login-stage label: yes if suspicious downstream behaviour occurs

- `relinquished-account access and operation`
  - login-stage label: yes if the access context is already suspicious
  - post-login-stage label: yes if sustained behavioural misuse is present

- `suspicious downstream misuse after successful access`
  - login-stage label: not necessarily
  - post-login-stage label: yes

## Scenario injection design for version 1

The first version of the shared dataset should be mostly legitimate behaviour with a smaller but meaningful proportion of suspicious cases.

The design goal is:

- enough fraud to support learning and evaluation
- enough legitimate-but-unusual behaviour to create realistic false-positive pressure

### Recommended high-level composition

A reasonable starting point is:

- majority normal and low-risk behaviour
- smaller share of legitimate but unusual behaviour
- minority share of fraud scenarios

Illustrative starting split:

- 65% to 75% normal returning-user login and normal usage
- 10% to 20% legitimate but unusual behaviour
- 10% to 20% fraud scenarios

This does not need to be final. It is a practical version 1 starting point.

### Recommended fraud scenario balance

A reasonable starting distribution inside the fraud subset is:

- social engineering or malicious approval -> high
- remote-control or device-compromise access -> medium
- repeated attempts before success -> medium
- relinquished-account access and operation -> medium
- suspicious downstream misuse after successful access -> high for project 2 coverage

Why this balance works:

- it gives project 1 enough login-stage fraud variation
- it gives project 2 enough downstream misuse variation
- it avoids concentrating too much of the dataset into one easy fraud pattern

## Project-specific consumption of shared labels

Although the dataset is shared, the two projects do not consume labels in the same way.

### Project 1 consumption

Project 1 should consume:

- event-level labels
- login-stage fraud outcomes

Its scored rows are mainly:

- `qr_login_approved`
- `app_login_success`
- other decisive login or approval outcomes

### Project 2 consumption

Project 2 should consume:

- session-level labels
- downstream misuse outcomes

Its scored units are mainly:

- authenticated sessions
- post-login event sequences
- account behaviour over time

## Recommended implementation simplification

To keep version 1 manageable, the data generator should start with one label source of truth and then derive project-specific views from it.

Recommended approach:

1. Generate scenarios at the session level.
2. Assign a scenario to each synthetic session.
3. Derive:
   - event-level fraud labels for project 1
   - session-level fraud labels for project 2

This is simpler than generating two completely separate labelling systems.

## What this shared simulation is trying to test

The shared simulation is intended to test whether the portfolio can:

- distinguish suspicious access from legitimate but unusual access
- detect technically valid yet behaviourally suspicious login events
- detect suspicious downstream usage after access is obtained
- model both one-off compromise and sustained account misuse
- support both preventive and containment-style fraud controls

## What is intentionally deferred

The shared scenario universe is still version 1.

The following can be added later if needed:

- richer recovery-led scenarios
- more detailed Myinfo misuse variants
- more detailed signing misuse variants
- explicit investigation or support-intervention flows

## Next step

If this shared scenario universe looks right, the next step is implementation planning for the synthetic data generator.

That implementation should use this document to define:

- session-generation logic
- event-sequence templates
- fraud label derivation
- project-specific training views for project 1 and project 2
