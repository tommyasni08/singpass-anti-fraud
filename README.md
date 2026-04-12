# Singpass Anti-Fraud Portfolio

This repository is a portfolio project that explores anti-fraud detection for a Singpass-like digital identity environment.

The portfolio is built around two complementary objectives:

- minimise compromise of accounts at the point of live login
- minimise damage after compromise through active monitoring

The work is intentionally structured to resemble a real fraud program rather than a single isolated notebook or model.

## Repository structure

- [initial_research](/Users/tommyasni08/Documents/Projects/singpass-anti-fraud/initial_research/initial_research.md)
  - product and abuse-context research used to scope the portfolio
- [pre_requisites](/Users/tommyasni08/Documents/Projects/singpass-anti-fraud/pre_requisites)
  - shared event taxonomy, schema design, backend design, scenario design, and portfolio architecture
- [data](/Users/tommyasni08/Documents/Projects/singpass-anti-fraud/data/README.md)
  - shared synthetic data generator and generated backend tables
- [singpass-login-risk-engine](/Users/tommyasni08/Documents/Projects/singpass-anti-fraud/singpass-login-risk-engine/README.md)
  - project 1: live login risk detection
- [singpass-post-compromise-monitoring](/Users/tommyasni08/Documents/Projects/singpass-anti-fraud/singpass-post-compromise-monitoring/README.md)
  - project 2: post-login misuse detection and damage containment

## Portfolio design

The repository uses one shared synthetic backend for both projects.

That shared environment includes:

- users
- devices
- user-device relationships
- services
- sessions
- events
- fraud labels

This allows both projects to operate on the same simulated identity system:

- project 1 focuses on suspicious live access
- project 2 focuses on suspicious downstream behaviour after access is granted

## Why this portfolio exists

The research for this portfolio narrowed the most relevant abuse patterns to:

- fraudulent account creation in downstream financial services
- sale or relinquishment of Singpass accounts or credentials
- stolen or deceptively obtained Singpass credentials

These patterns suggest that a realistic anti-fraud design needs both:

- a login-stage risk engine
- a post-login monitoring and containment layer

## Current project status

### Project 1: Singpass Login Risk Engine

Project 1 is implemented as a full scoring pipeline:

- shared synthetic data input
- feature engineering
- rule-based scoring
- XGBoost ML scoring
- tuned hybrid decision policy

Project 1 output:

- [project README](/Users/tommyasni08/Documents/Projects/singpass-anti-fraud/singpass-login-risk-engine/README.md)
- [project plan](/Users/tommyasni08/Documents/Projects/singpass-anti-fraud/singpass-login-risk-engine/project_plan.md)

Current final project-1 comparison:

| Approach | Review Rate | Recall | Precision |
| --- | ---: | ---: | ---: |
| Rule-only | 10.81% | 78.05% | 80.14% |
| ML-only (`ml_score >= 0.5`) | 12.05% | 88.70% | 81.76% |
| Hybrid v3 | 10.46% | 80.96% | 85.93% |

The final selected decision layer for project 1 is the tuned hybrid policy because it satisfies the chosen operational target:

- review rate under `12%`
- precision above `85%`
- highest recall found under those constraints

### Project 2: Singpass Post-Compromise Monitoring

Project 2 is implemented as a full session-level monitoring pipeline:

- shared synthetic data input
- session-level feature engineering
- rule-based post-login containment logic
- narrowed behavioural XGBoost scoring
- recall-first hybrid containment policy

Project 2 outputs:

- [project README](/Users/tommyasni08/Documents/Projects/singpass-anti-fraud/singpass-post-compromise-monitoring/README.md)
- [project plan](/Users/tommyasni08/Documents/Projects/singpass-anti-fraud/singpass-post-compromise-monitoring/project_plan.md)

Current final project-2 comparison:

| Approach | Review Rate | Recall | Precision |
| --- | ---: | ---: | ---: |
| Rule-only | 12.89% | 74.07% | 100.00% |
| ML-only (`ml_score >= 0.5`) | 14.46% | 83.07% | 99.96% |
| Hybrid v1 (`rule OR ml_score >= 0.3`) | 18.08% | 99.48% | 95.73% |

The final selected decision layer for project 2 is the recall-first hybrid policy because containment recall is the main operating priority.

## Shared prerequisites

The following documents define the shared system before project-specific modeling begins:

- [Singpass event taxonomy](/Users/tommyasni08/Documents/Projects/singpass-anti-fraud/pre_requisites/singpass_event_taxonomy.md)
- [Data schema](/Users/tommyasni08/Documents/Projects/singpass-anti-fraud/pre_requisites/data_schema.md)
- [Backend table design](/Users/tommyasni08/Documents/Projects/singpass-anti-fraud/pre_requisites/backend_table_design.md)
- [Shared simulation scenarios](/Users/tommyasni08/Documents/Projects/singpass-anti-fraud/pre_requisites/shared_simulation_scenarios.md)
- [Portfolio architecture](/Users/tommyasni08/Documents/Projects/singpass-anti-fraud/pre_requisites/portfolio_architecture.md)

## Synthetic data

The shared synthetic data layer is generated from the scripts under [data](/Users/tommyasni08/Documents/Projects/singpass-anti-fraud/data/README.md).

This layer is meant to mimic a minimum viable backend environment for both projects, not just produce flat training files.

## Recommended reading order

1. [initial_research](/Users/tommyasni08/Documents/Projects/singpass-anti-fraud/initial_research/initial_research.md)
2. [portfolio_architecture](/Users/tommyasni08/Documents/Projects/singpass-anti-fraud/pre_requisites/portfolio_architecture.md)
3. [singpass-login-risk-engine](/Users/tommyasni08/Documents/Projects/singpass-anti-fraud/singpass-login-risk-engine/README.md)
4. [singpass-post-compromise-monitoring](/Users/tommyasni08/Documents/Projects/singpass-anti-fraud/singpass-post-compromise-monitoring/README.md)

## Scope note

This repository is not intended to reproduce actual Singpass internals.

It is a portfolio-grade simulation and anti-fraud design exercise built from publicly researched product understanding, a shared synthetic backend, and project-level decisioning pipelines.
