# Hybrid Evaluation Report

Last updated: 12 April 2026

## Dataset summary

- hybrid policy version: v3
- operating target: review rate under 12%, maximize recall, precision above 85%
- total rows: 39,538
- fraud rows: 4,391
- hybrid review rows: 4,137
- hybrid review fraud rows: 3,555
- hybrid review rate: 10.46%
- hybrid recall on fraud rows: 80.96%
- hybrid precision on review rows: 85.93%

## Action summary

- `allow`: rows=34,687, fraud_rows=457, fraud_rate=1.32%
- `allow_with_monitoring`: rows=714, fraud_rows=379, fraud_rate=53.08%
- `step_up`: rows=102, fraud_rows=50, fraud_rate=49.02%
- `step_up_or_manual_review`: rows=2,301, fraud_rows=1,783, fraud_rate=77.49%
- `block_or_manual_review`: rows=1,734, fraud_rows=1,722, fraud_rate=99.31%

## Hybrid risk-band summary

- `low`: rows=34,687, fraud_rows=457, fraud_rate=1.32%
- `medium`: rows=801, fraud_rows=418, fraud_rate=52.18%
- `high`: rows=2,316, fraud_rows=1,794, fraud_rate=77.46%
- `critical`: rows=1,734, fraud_rows=1,722, fraud_rate=99.31%

## Rule band x ML bucket grid

- `low x <0.3`: rows=34,383, fraud_rows=456, fraud_rate=1.33%
- `low x 0.3-0.5`: rows=87, fraud_rows=39, fraud_rate=44.83%
- `low x 0.5-0.8`: rows=4, fraud_rows=3, fraud_rate=75.00%
- `low x 0.8-0.93`: rows=0, fraud_rows=0, fraud_rate=0.00%
- `low x >=0.93`: rows=315, fraud_rows=312, fraud_rate=99.05%
- `medium x <0.3`: rows=246, fraud_rows=0, fraud_rate=0.00%
- `medium x 0.3-0.5`: rows=58, fraud_rows=1, fraud_rate=1.72%
- `medium x 0.5-0.8`: rows=16, fraud_rows=11, fraud_rate=68.75%
- `medium x 0.8-0.93`: rows=8, fraud_rows=2, fraud_rate=25.00%
- `medium x >=0.93`: rows=145, fraud_rows=140, fraud_rate=96.55%
- `high x <0.3`: rows=0, fraud_rows=0, fraud_rate=0.00%
- `high x 0.3-0.5`: rows=0, fraud_rows=0, fraud_rate=0.00%
- `high x 0.5-0.8`: rows=0, fraud_rows=0, fraud_rate=0.00%
- `high x 0.8-0.93`: rows=7, fraud_rows=2, fraud_rate=28.57%
- `high x >=0.93`: rows=893, fraud_rows=886, fraud_rate=99.22%
- `critical x <0.3`: rows=0, fraud_rows=0, fraud_rate=0.00%
- `critical x 0.3-0.5`: rows=0, fraud_rows=0, fraud_rate=0.00%
- `critical x 0.5-0.8`: rows=5, fraud_rows=0, fraud_rate=0.00%
- `critical x 0.8-0.93`: rows=705, fraud_rows=376, fraud_rate=53.33%
- `critical x >=0.93`: rows=2,666, fraud_rows=2,163, fraud_rate=81.13%

## Notes

- The hybrid layer is a policy combiner, not an averaged score.
- Hybrid v3 adds a small second-round escalation on selected medium-risk ML pockets while staying inside the operating target.
- This version was chosen because it improves recall over v2 while keeping review rate under 12% and precision above 85%.
