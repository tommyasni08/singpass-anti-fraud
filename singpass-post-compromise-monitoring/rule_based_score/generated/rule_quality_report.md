# Rule Quality Report

Last updated: 12 April 2026

## Dataset summary

- scored rows: 38,834
- fraud rows: 6,757
- flagged rows: 5,151
- flagged fraud rows: 5,151
- rule-layer flag rate: 13.26%
- rule-layer recall on fraud rows: 76.23%
- rule-layer precision on flagged rows: 100.00%
- review-threshold rows (score >= 3): 5,005
- review-threshold fraud rows: 5,005
- review-threshold rate: 12.89%
- review-threshold recall on fraud rows: 74.07%
- review-threshold precision: 100.00%

## Rule hit summary

- `R01_consent_granted_in_session`: hits=841, fraud_hits=841, precision=100.00%
- `R02_signing_completed_in_session`: hits=905, fraud_hits=905, precision=100.00%
- `R03_stacked_sensitive_activity`: hits=1,556, fraud_hits=1,556, precision=100.00%
- `R04_sensitive_session_with_service_switching`: hits=1,556, fraud_hits=1,556, precision=100.00%
- `R05_sensitive_session_without_benign_usage`: hits=5,151, fraud_hits=5,151, precision=100.00%
- `R06_high_burst_sensitive_session`: hits=476, fraud_hits=476, precision=100.00%
- `R07_first_time_sensitive_flow`: hits=4,751, fraud_hits=4,751, precision=100.00%

## Risk-band summary

- `low`: rows=33,683, fraud_rows=1,606, fraud_rate=4.77%
- `medium`: rows=146, fraud_rows=146, fraud_rate=100.00%
- `high`: rows=1,969, fraud_rows=1,969, fraud_rate=100.00%
- `critical`: rows=3,036, fraud_rows=3,036, fraud_rate=100.00%

## Assessment

- The rule layer is expected to be strong in project 2 because explicit downstream misuse is part of the post-login monitoring problem.
- The review threshold should still be evaluated operationally rather than assumed to be final.
- If the rule layer is already too close to deterministic, the ML layer should avoid over-relying on the same direct session summaries.
