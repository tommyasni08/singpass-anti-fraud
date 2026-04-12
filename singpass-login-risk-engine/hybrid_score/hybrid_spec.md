# Hybrid Specification

Last updated: 12 April 2026

## Purpose

This document defines how the rule-based and ML-based scores are combined for the Singpass Login Risk Engine.

The hybrid layer is a policy layer, not a mathematical average.

Why:

- the rule layer expresses explicit operational logic
- the ML layer expresses probabilistic pattern risk
- the two outputs do not have the same semantics

So the right approach is:

- preserve rules for clear hard signals
- use ML for broader probabilistic support
- combine them through a decision policy

## Inputs

The hybrid layer joins two upstream outputs on `event_id`:

- `rule_based_score/generated/login_rule_scores.csv`
- `ml_based_score/generated/login_ml_scores.csv`

## Policy design

### Rule role

The rule layer should dominate when the rule evidence is explicit and strong.

In the current tuned rule baseline:

- `critical` rule band is highly actionable
- `high` rule band is strong review signal

### ML role

The ML layer should add coverage where:

- rule evidence is weaker
- the login looks suspicious as a combination of softer signals

## Tuned hybrid v3 thresholds

ML thresholds:

- `ml_score >= 0.93` -> direct high-risk review candidate
- `0.50 <= ml_score < 0.93` -> monitoring or conditional escalation range
- `0.30 <= ml_score < 0.50` -> low-to-mid risk range used only in a narrow escalation pocket

Strong-rule conditions:

- any row containing `R02_repeated_rejection_pressure`
- any row containing `R03_high_attempt_volume_before_success`
- exact `R06_fast_approval_with_novelty`
- exact `R01_fast_qr_approval`

These rule cases were selected because they showed very high precision in the tuning analysis.

## Tuned hybrid v3 policy

### 1. Critical block / manual review

Condition:

- strong-rule condition
- and `ml_score >= 0.93`

Action:

- `block_or_manual_review`

Reason:

- rule evidence is already explicit enough

### 2. Strong review / step-up

Condition:

- strong-rule condition
or
- `ml_score >= 0.93`

Action:

- `step_up_or_manual_review`

Reason:

- either the rules are already strong or the ML score is very high

### 3. Targeted escalation pockets

Conditions:

- `rule_risk_band = medium` and `0.50 <= ml_score < 0.80`
- `rule_risk_band = low` and `0.30 <= ml_score < 0.50`

Actions:

- `step_up`

Reason:

- these pockets improved recall during tuning while keeping the operating target intact

### 4. Monitoring only

Condition:

- `ml_score >= 0.50`

Action:

- `allow_with_monitoring`

### 5. Allow

Condition:

- everything else

Action:

- `allow`

## Output columns

Recommended fields:

- `event_id`
- `target_login_fraud_flag`
- `fraud_scenario`
- `rule_score`
- `rule_risk_band`
- `ml_score`
- `ml_predicted_flag`
- `hybrid_risk_band`
- `hybrid_action`
- `hybrid_review_flag`

## Evaluation focus

The first hybrid evaluation should answer:

- how many rows are pushed into each action bucket
- what fraud rate exists in each bucket
- whether the hybrid policy improves the balance between review rate and fraud capture

## Why this tuned version was chosen

The earlier hybrid policy was too close to ML-only and did not use rule evidence selectively enough.

Hybrid v3 was selected because it best fits the current operating target:

- review rate under `12%`
- precision above `85%`
- maximize recall subject to those constraints

Final selected operating point:

- review rate: `10.46%`
- recall: `80.96%`
- precision: `85.93%`

## Design principle

The hybrid layer remains:

- policy-based
- auditable
- easy to tune

It is still not:

- a meta-model
- a weighted average
- a black-box ensemble
