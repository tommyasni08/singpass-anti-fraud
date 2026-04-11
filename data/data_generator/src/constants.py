ACCOUNT_STATUSES = ["active", "locked", "suspended", "inactive"]
AGE_BANDS = ["18_24", "25_34", "35_49", "50_64", "65_plus"]
PRIMARY_REGIONS = ["SG_CENTRAL", "SG_EAST", "SG_WEST", "SG_NORTH", "SG_NORTHEAST"]
LOGIN_FREQUENCY_BANDS = ["low", "medium", "high"]
TRAVEL_PROFILES = ["local_only", "occasional_travel", "frequent_travel"]

OS_TYPES = ["ios", "android"]
DEVICE_STATUSES = ["active", "inactive", "replaced", "flagged"]
TRUST_STATUSES = ["trusted", "new", "revoked", "stale"]

SECTOR_TYPES = ["government", "banking", "insurance", "telecom", "other_private"]
RISK_TIERS = ["low", "medium", "high"]

SESSION_STATUSES = ["completed", "abandoned", "failed", "restricted"]
LOGIN_METHODS = ["qr_login", "app_login", "face_verification"]

EVENT_CATEGORIES = [
    "login_authentication",
    "account_device_lifecycle",
    "consent_data_sharing",
    "digital_signing_authorisation",
    "recovery",
]

CHANNELS = ["mobile_app", "desktop_web", "mobile_web", "api"]
EVENT_RESULTS = ["success", "failure", "rejected", "cancelled", "timeout", "completed"]

FRAUD_STAGES = ["login_stage", "post_login_stage"]

SCENARIO_NAMES = [
    "normal_returning_login_and_normal_usage",
    "legitimate_travel_or_device_change_login",
    "legitimate_first_time_or_infrequent_service_usage",
    "social_engineering_or_malicious_approval",
    "remote_control_or_device_compromise_access",
    "repeated_attempts_before_success",
    "relinquished_account_access_and_operation",
    "suspicious_downstream_misuse_after_successful_access",
]
