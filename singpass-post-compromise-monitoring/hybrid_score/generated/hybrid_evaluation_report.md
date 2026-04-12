# Hybrid Evaluation Report

Last updated: 12 April 2026

## Dataset summary

- hybrid policy version: v1
- operating priority: maximize containment recall
- total rows: 38,834
- fraud rows: 6,757
- hybrid review rows: 7,022
- hybrid review fraud rows: 6,722
- hybrid review rate: 18.08%
- hybrid recall on fraud rows: 99.48%
- hybrid precision on review rows: 95.73%

## Action summary

- `allow`: rows=31,812, fraud_rows=35, fraud_rate=0.11%
- `review_due_to_behavioral_risk`: rows=2,017, fraud_rows=1,717, fraud_rate=85.13%
- `manual_review`: rows=1,969, fraud_rows=1,969, fraud_rate=100.00%
- `restrict_or_manual_review`: rows=3,036, fraud_rows=3,036, fraud_rate=100.00%

## Notes

- The hybrid policy reviews any session that either matches the tuned rule layer or has `ml_score >= 0.3`.
- This operating point was selected because project 2 prioritizes containment recall over minimizing review volume.
