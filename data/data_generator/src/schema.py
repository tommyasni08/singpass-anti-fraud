from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any


@dataclass
class UserRecord:
    user_id: str
    user_created_at: datetime
    account_status: str
    account_age_days: int
    age_band: str
    primary_region: str
    baseline_login_frequency_band: str
    baseline_travel_profile: str


@dataclass
class DeviceRecord:
    device_id: str
    device_first_seen_at: datetime
    os_type: str
    os_version: str
    app_version: str
    biometric_capable_flag: bool
    device_status: str
    rooted_or_compromised_flag: bool
    emulator_flag: bool


@dataclass
class UserDeviceRecord:
    user_device_id: str
    user_id: str
    device_id: str
    linked_at: datetime
    unlinked_at: datetime | None
    is_primary_device_flag: bool
    trust_status: str
    last_seen_at: datetime


@dataclass
class ServiceRecord:
    service_id: str
    service_name: str
    sector_type: str
    risk_tier: str
    supports_myinfo_flag: bool
    supports_signing_flag: bool


@dataclass
class SessionRecord:
    session_id: str
    user_id: str
    device_id: str
    service_id: str
    session_start_at: datetime
    session_end_at: datetime
    session_status: str
    login_method: str
    authenticated_flag: bool


@dataclass
class EventRecord:
    event_id: str
    event_timestamp: datetime
    event_category: str
    event_type: str
    user_id: str
    device_id: str | None
    service_id: str | None
    session_id: str | None
    ip_address: str
    asn: str
    country: str
    region: str
    channel: str
    event_result: str
    approval_latency_seconds: float | None
    event_metadata_json: dict[str, Any]


@dataclass
class FraudLabelRecord:
    label_id: str
    event_id: str
    user_id: str
    label_timestamp: datetime
    is_fraud_flag: bool
    fraud_scenario: str
    fraud_stage: str
    downstream_damage_flag: bool
