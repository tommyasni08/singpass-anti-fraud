# ML Evaluation Report

Last updated: 12 April 2026

## Model setup

- baseline model: XGBoost classifier
- runtime environment: Python 3.11 project virtual environment
- split strategy: earliest 80% train, latest 20% evaluation by login timestamp
- categorical handling: one-hot encoding
- class weighting: `scale_pos_weight` derived from train fraud rate

## Split summary

- train rows: 31,067
- evaluation rows: 7,767
- train fraud rate: 17.51%
- evaluation fraud rate: 16.96%

## Train metrics by threshold

- threshold 0.3: precision=95.65%, recall=85.64%, accuracy=96.80%, tp/fp/fn/tn=4659/212/781/25415
- threshold 0.5: precision=99.98%, recall=82.72%, accuracy=96.97%, tp/fp/fn/tn=4500/1/940/25626
- threshold 0.7: precision=100.00%, recall=82.48%, accuracy=96.93%, tp/fp/fn/tn=4487/0/953/25627

## Evaluation metrics by threshold

- threshold 0.3: precision=92.68%, recall=84.66%, accuracy=96.27%, tp/fp/fn/tn=1115/88/202/6362
- threshold 0.5: precision=99.91%, recall=84.51%, accuracy=97.36%, tp/fp/fn/tn=1113/1/204/6449
- threshold 0.7: precision=100.00%, recall=84.51%, accuracy=97.37%, tp/fp/fn/tn=1113/0/204/6450

## Top feature importance

- `cat__login_country_SG`: 0.356566
- `num__time_to_first_service_switch_seconds`: 0.180453
- `num__distinct_service_count_in_session`: 0.164123
- `cat__login_country_ID`: 0.059692
- `cat__login_country_MY`: 0.057498
- `cat__login_country_TH`: 0.052929
- `num__time_to_first_service_switch_missing_flag`: 0.047167
- `cat__trust_status_trusted`: 0.003488
- `cat__login_method_face_verification`: 0.003293
- `cat__service_sector_type_banking`: 0.003098

## Notes

- This baseline intentionally excludes the clearest direct post-login completion flags already covered by the rule layer.
- The purpose of this model is to test whether broader session-shape and behavioural features add value beyond explicit containment rules.
