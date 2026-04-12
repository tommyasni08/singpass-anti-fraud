# Hybrid Specification

Last updated: 12 April 2026

## Purpose

This document defines how the rule-based and ML-based scores are combined for the Singpass Post-Compromise Monitoring project.

The hybrid layer is a policy layer, not a mathematical average.

Why:

- the rule layer expresses explicit downstream containment logic
- the ML layer expresses broader behavioural misuse risk
- the two outputs do not have the same semantics

## Inputs

The hybrid layer joins two upstream outputs on `session_id`:

- `rule_based_score/generated/post_login_rule_scores.csv`
- `ml_based_score/generated/post_login_ml_scores.csv`

## Operating priority

Project 2 prioritizes:

- maximizing containment recall

This means the hybrid policy is allowed to review more sessions than the project-1 login policy, as long as the added review volume is buying meaningful fraud capture.

## Selected operating point

The chosen first operating point is:

- keep all rule-review sessions
- additionally review sessions with `ml_score >= 0.3`

Why this threshold was selected:

- `0.2` increased review rate too sharply and reduced precision too much
- `0.3` preserved very high precision while pushing recall close to full coverage
- higher thresholds such as `0.4` or `0.5` were cleaner, but gave up avoidable fraud capture

## Hybrid v1 policy

### 1. Hard containment

Condition:

- `rule_risk_band = critical`

Action:

- `restrict_or_manual_review`

### 2. Strong review

Condition:

- `rule_review_flag = 1`

Action:

- `manual_review`

### 3. Behavioural review

Condition:

- `rule_review_flag = 0`
- `ml_score >= 0.3`

Action:

- `review_due_to_behavioral_risk`

### 4. Allow

Condition:

- everything else

Action:

- `allow`

## Output columns

Recommended fields:

- `session_id`
- `target_post_login_fraud_flag`
- `dominant_fraud_scenario`
- `rule_score`
- `rule_risk_band`
- `ml_score`
- `ml_predicted_flag`
- `hybrid_risk_band`
- `hybrid_action`
- `hybrid_review_flag`

## Why this policy is appropriate for project 2

Project 2 is a containment problem.

That means:

- missing a fraud session is more costly than reviewing an additional suspicious session
- the hybrid layer should lean toward broader fraud capture than the project-1 login-risk policy

## Current selected result

Hybrid v1 at `ml_score >= 0.3` achieves:

- review rate: `18.08%`
- recall: `99.48%`
- precision: `95.73%`

This is the correct starting point for a recall-first post-login monitoring system.
