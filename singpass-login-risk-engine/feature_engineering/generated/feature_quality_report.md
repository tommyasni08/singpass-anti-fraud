# Feature Quality Report

Last updated: 12 April 2026

## Dataset summary

- rows: 39,538
- fraud rows: 4,391
- non-fraud rows: 35,147
- fraud rate: 0.1111

## Scored login event types

- `app_login_success`: 17,704
- `qr_login_approved`: 21,834

## Scenario distribution

- `legitimate_first_time_or_infrequent_service_usage`: 2,025
- `legitimate_travel_or_device_change_login`: 3,956
- `normal_returning_login_and_normal_usage`: 26,096
- `relinquished_account_access_and_operation`: 1,556
- `remote_control_or_device_compromise_access`: 1,606
- `repeated_attempts_before_success`: 704
- `social_engineering_or_malicious_approval`: 2,436
- `suspicious_downstream_misuse_after_successful_access`: 1,159

## Null-rate summary

- `days_since_last_successful_login`: 5,000 null/blank values (12.65%)
- `approval_latency_missing_flag`: 0 null/blank values (0.00%)
- `approval_latency_seconds`: 0 null/blank values (0.00%)
- `asn`: 0 null/blank values (0.00%)
- `channel`: 0 null/blank values (0.00%)
- `country`: 0 null/blank values (0.00%)
- `days_since_device_linked`: 0 null/blank values (0.00%)
- `days_since_last_successful_login_missing_flag`: 0 null/blank values (0.00%)
- `days_since_user_device_last_seen`: 0 null/blank values (0.00%)
- `device_id`: 0 null/blank values (0.00%)
- `device_prior_distinct_users_30d`: 0 null/blank values (0.00%)
- `device_prior_login_count_30d`: 0 null/blank values (0.00%)
- `device_used_by_multiple_users_flag`: 0 null/blank values (0.00%)
- `event_id`: 0 null/blank values (0.00%)
- `event_result`: 0 null/blank values (0.00%)
- `event_timestamp`: 0 null/blank values (0.00%)
- `first_time_service_for_user_flag`: 0 null/blank values (0.00%)
- `fraud_scenario`: 0 null/blank values (0.00%)
- `ip_address`: 0 null/blank values (0.00%)
- `is_primary_device_flag`: 0 null/blank values (0.00%)
- `login_event_type`: 0 null/blank values (0.00%)
- `login_hour_of_day`: 0 null/blank values (0.00%)
- `login_method`: 0 null/blank values (0.00%)
- `new_asn_for_user_flag`: 0 null/blank values (0.00%)
- `new_country_for_user_flag`: 0 null/blank values (0.00%)
- `new_region_for_user_flag`: 0 null/blank values (0.00%)
- `region`: 0 null/blank values (0.00%)
- `service_id`: 0 null/blank values (0.00%)
- `service_risk_tier`: 0 null/blank values (0.00%)
- `service_sector_type`: 0 null/blank values (0.00%)
- `service_supports_myinfo_flag`: 0 null/blank values (0.00%)
- `service_supports_signing_flag`: 0 null/blank values (0.00%)
- `service_usage_count_by_user_30d`: 0 null/blank values (0.00%)
- `service_used_by_user_last_30d_flag`: 0 null/blank values (0.00%)
- `session_event_count_before_login`: 0 null/blank values (0.00%)
- `session_failed_login_events_before_login`: 0 null/blank values (0.00%)
- `session_has_contact_detail_updated_before_login_flag`: 0 null/blank values (0.00%)
- `session_has_lifecycle_event_before_login_flag`: 0 null/blank values (0.00%)
- `session_id`: 0 null/blank values (0.00%)
- `session_lifecycle_event_count_before_login`: 0 null/blank values (0.00%)
- `session_qr_prompt_count_before_login`: 0 null/blank values (0.00%)
- `session_qr_request_count_before_login`: 0 null/blank values (0.00%)
- `session_rejected_login_events_before_login`: 0 null/blank values (0.00%)
- `target_login_fraud_flag`: 0 null/blank values (0.00%)
- `trust_status`: 0 null/blank values (0.00%)
- `user_device_link_exists_flag`: 0 null/blank values (0.00%)
- `user_id`: 0 null/blank values (0.00%)
- `user_prior_distinct_asns_30d`: 0 null/blank values (0.00%)
- `user_prior_distinct_countries_30d`: 0 null/blank values (0.00%)
- `user_prior_distinct_services_30d`: 0 null/blank values (0.00%)
- `user_prior_login_count_7d`: 0 null/blank values (0.00%)
- `user_prior_rejected_login_count_7d`: 0 null/blank values (0.00%)
- `user_prior_successful_login_count_7d`: 0 null/blank values (0.00%)

## Inspection summary

- The current feature table is sufficient to proceed to a first hybrid baseline.
- There is already clear separation signal for both rules and ML in latency, repeated-attempt context, and novelty-style features.
- The current weak area is lifecycle-related precursor context, which is sparse because the generator mostly emits lifecycle events after login.

## Numeric feature inspection

- `approval_latency_seconds`
  fraud mean/median: 2.55 / 1.50
  non-fraud mean/median: 10.76 / 10.80
- `session_rejected_login_events_before_login`
  fraud mean/median: 0.47 / 0.00
  non-fraud mean/median: 0.00 / 0.00
- `session_qr_request_count_before_login`
  fraud mean/median: 1.00 / 1.00
  non-fraud mean/median: 0.56 / 1.00
- `user_prior_login_count_7d`
  fraud mean/median: 0.80 / 0.00
  non-fraud mean/median: 0.32 / 0.00
- `user_prior_rejected_login_count_7d`
  fraud mean/median: 0.51 / 0.00
  non-fraud mean/median: 0.03 / 0.00
- `device_prior_login_count_30d`
  fraud mean/median: 1.02 / 1.00
  non-fraud mean/median: 1.02 / 1.00
- `service_usage_count_by_user_30d`
  fraud mean/median: 0.10 / 0.00
  non-fraud mean/median: 0.10 / 0.00

## Boolean feature inspection

- `new_country_for_user_flag`: fraud positive rate 67.21%, non-fraud positive rate 46.51%
- `new_region_for_user_flag`: fraud positive rate 66.82%, non-fraud positive rate 46.50%
- `new_asn_for_user_flag`: fraud positive rate 83.97%, non-fraud positive rate 75.21%
- `user_device_link_exists_flag`: fraud positive rate 100.00%, non-fraud positive rate 100.00%
- `first_time_service_for_user_flag`: fraud positive rate 90.84%, non-fraud positive rate 90.95%
- `device_used_by_multiple_users_flag`: fraud positive rate 0.00%, non-fraud positive rate 0.00%
- `days_since_last_successful_login_missing_flag`: fraud positive rate 12.30%, non-fraud positive rate 12.69%

## Categorical feature inspection

- `login_event_type`
  fraud top values: qr_login_approved (52.2%), app_login_success (47.8%)
  non-fraud top values: qr_login_approved (55.6%), app_login_success (44.4%)
- `login_method`
  fraud top values: qr_login (52.2%), app_login (41.1%), face_verification (6.7%)
  non-fraud top values: qr_login (55.6%), app_login (34.9%), face_verification (9.5%)
- `service_risk_tier`
  fraud top values: low (41.7%), high (33.5%), medium (24.8%)
  non-fraud top values: low (41.8%), high (33.1%), medium (25.1%)
- `trust_status`
  fraud top values: trusted (79.2%), new (9.7%), stale (8.0%), revoked (3.1%)
  non-fraud top values: trusted (80.3%), new (9.5%), stale (7.3%), revoked (3.0%)
- `country`
  fraud top values: SG (48.2%), MY (18.0%), TH (17.1%), ID (16.7%)
  non-fraud top values: SG (86.3%), ID (4.6%), TH (4.6%), MY (4.5%)

## Hybrid baseline assessment

- Rule-ready features already exist for repeated-attempt patterns through `session_rejected_login_events_before_login` and `session_qr_request_count_before_login`.
- Rule-ready features also exist for suspiciously fast approvals through `approval_latency_seconds`.
- ML-ready contextual variation exists in service sensitivity, trust status, novelty flags, and short-window history counts.
- The current table is strong enough for a first rule baseline and a simple tree-based model.
- Additional feature passes are still useful later, but they are not required before the first baseline.

## Notes

- Null and blank values are expected for some time-delta or relationship-derived features.
- This first pass uses only information available at or before the decisive login event timestamp.
- Lifecycle-related precursor features are expected to be sparse in version 1 because the current generator mostly emits lifecycle events after login success.
