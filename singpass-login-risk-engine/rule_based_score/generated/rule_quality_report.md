# Rule Quality Report

Last updated: 12 April 2026

## Dataset summary

- scored rows: 39,538
- fraud rows: 4,391
- flagged rows: 4,749
- flagged fraud rows: 3,581
- rule-layer flag rate: 12.01%
- rule-layer recall on fraud rows: 81.55%
- rule-layer precision on flagged rows: 75.41%
- review-threshold rows (score >= 3): 4,276
- review-threshold fraud rows: 3,427
- review-threshold rate: 10.81%
- review-threshold recall on fraud rows: 78.05%
- review-threshold precision: 80.14%

## Rule hit summary

- `R01_fast_qr_approval`: hits=2,622, fraud_hits=2,027, precision=77.31%
- `R02_repeated_rejection_pressure`: hits=704, fraud_hits=704, precision=100.00%
- `R03_high_attempt_volume_before_success`: hits=392, fraud_hits=392, precision=100.00%
- `R04_foreign_and_new_country`: hits=2,926, fraud_hits=2,117, precision=72.35%
- `R06_fast_approval_with_novelty`: hits=4,251, fraud_hits=3,402, precision=80.03%
- `R07_prior_rejection_history_plus_success`: hits=1,068, fraud_hits=750, precision=70.22%

## Risk-band summary

- `low`: rows=34,789, fraud_rows=810, fraud_rate=2.33%
- `medium`: rows=473, fraud_rows=154, fraud_rate=32.56%
- `high`: rows=900, fraud_rows=888, fraud_rate=98.67%
- `critical`: rows=3,376, fraud_rows=2,539, fraud_rate=75.21%

## Assessment

- The rule layer is intended to catch the clearest suspicious access patterns, not every fraud case.
- High precision on specific rules is more important than broad coverage for the first baseline.
- The ML layer absorbs weaker, multi-feature patterns that do not warrant hard rules on their own.
- For operations, `score >= 3` is the more realistic review threshold than `any hit`.
