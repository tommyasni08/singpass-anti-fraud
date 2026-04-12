# ML Evaluation Report

Last updated: 11 April 2026

## Model setup

- baseline model: XGBoost classifier
- runtime environment: Python 3.11 project virtual environment
- split strategy: earliest 80% train, latest 20% evaluation by event timestamp
- categorical handling: one-hot encoding
- class weighting: `scale_pos_weight` derived from train fraud rate

## Split summary

- train rows: 31,630
- evaluation rows: 7,908
- train fraud rate: 11.23%
- evaluation fraud rate: 10.60%

## Train metrics by threshold

- threshold 0.3: precision=80.65%, recall=89.98%, accuracy=96.45%, tp/fp/fn/tn=3197/767/356/27310
- threshold 0.5: precision=82.08%, recall=88.94%, accuracy=96.58%, tp/fp/fn/tn=3160/690/393/27387
- threshold 0.7: precision=82.10%, recall=88.54%, accuracy=96.54%, tp/fp/fn/tn=3146/686/407/27391

## Evaluation metrics by threshold

- threshold 0.3: precision=78.10%, recall=88.07%, accuracy=96.12%, tp/fp/fn/tn=738/207/100/6863
- threshold 0.5: precision=80.42%, recall=87.71%, accuracy=96.43%, tp/fp/fn/tn=735/179/103/6891
- threshold 0.7: precision=80.59%, recall=87.71%, accuracy=96.46%, tp/fp/fn/tn=735/177/103/6893

## Top feature importance

- `approval_latency_seconds`: 0.418434
- `country_SG`: 0.061630
- `session_event_count_before_login`: 0.026853
- `session_rejected_login_events_before_login`: 0.022860
- `login_method_face_verification`: 0.021693
- `user_prior_rejected_login_count_7d`: 0.013980
- `service_supports_signing_flag`: 0.013845
- `service_supports_myinfo_flag`: 0.013659
- `trust_status_revoked`: 0.013299
- `service_risk_tier_low`: 0.013014

## Outputs

- `login_ml_scores.csv`
- `feature_importance.csv`
- `xgb_model.json`

## Notes

- XGBoost is a better fit than the earlier hand-rolled linear baseline for this tabular fraud problem.
- The next comparison step should align ML thresholds against the tuned rule review threshold rather than relying only on `0.5`.
