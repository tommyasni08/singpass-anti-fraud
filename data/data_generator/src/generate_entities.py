from __future__ import annotations

import random
from dataclasses import asdict
from datetime import datetime, timedelta

from .config import GeneratorConfig
from .constants import (
    ACCOUNT_STATUSES,
    AGE_BANDS,
    DEVICE_STATUSES,
    LOGIN_FREQUENCY_BANDS,
    OS_TYPES,
    PRIMARY_REGIONS,
    RISK_TIERS,
    SECTOR_TYPES,
    TRAVEL_PROFILES,
    TRUST_STATUSES,
)
from .schema import DeviceRecord, ServiceRecord, UserDeviceRecord, UserRecord


def _random_past_datetime(base: datetime, max_days_back: int) -> datetime:
    return base - timedelta(days=random.randint(0, max_days_back), minutes=random.randint(0, 1440))


def generate_users(config: GeneratorConfig, base_time: datetime) -> list[dict]:
    users: list[dict] = []
    for idx in range(1, config.num_users + 1):
        created_at = _random_past_datetime(base_time, 3650)
        users.append(
            asdict(
                UserRecord(
                    user_id=f"U{idx:06d}",
                    user_created_at=created_at,
                    account_status=random.choices(ACCOUNT_STATUSES, weights=[0.94, 0.02, 0.01, 0.03])[0],
                    account_age_days=max((base_time - created_at).days, 0),
                    age_band=random.choice(AGE_BANDS),
                    primary_region=random.choice(PRIMARY_REGIONS),
                    baseline_login_frequency_band=random.choice(LOGIN_FREQUENCY_BANDS),
                    baseline_travel_profile=random.choice(TRAVEL_PROFILES),
                )
            )
        )
    return users


def generate_devices_and_links(config: GeneratorConfig, users: list[dict], base_time: datetime) -> tuple[list[dict], list[dict]]:
    devices: list[dict] = []
    user_devices: list[dict] = []
    device_counter = 1
    link_counter = 1

    for user in users:
        num_devices = 1 if random.random() < 0.8 else 2
        if random.random() < 0.05:
            num_devices = 3
        for device_idx in range(num_devices):
            first_seen = _random_past_datetime(base_time, 1200)
            device_id = f"D{device_counter:06d}"
            devices.append(
                asdict(
                    DeviceRecord(
                        device_id=device_id,
                        device_first_seen_at=first_seen,
                        os_type=random.choice(OS_TYPES),
                        os_version=random.choice(["14", "15", "16", "17", "17.4"]),
                        app_version=random.choice(["12.1.0", "12.3.2", "13.0.1"]),
                        biometric_capable_flag=random.random() < 0.9,
                        device_status=random.choices(DEVICE_STATUSES, weights=[0.9, 0.04, 0.04, 0.02])[0],
                        rooted_or_compromised_flag=random.random() < 0.02,
                        emulator_flag=random.random() < 0.01,
                    )
                )
            )
            user_devices.append(
                asdict(
                    UserDeviceRecord(
                        user_device_id=f"UD{link_counter:06d}",
                        user_id=user["user_id"],
                        device_id=device_id,
                        linked_at=first_seen,
                        unlinked_at=None,
                        is_primary_device_flag=device_idx == 0,
                        trust_status=random.choices(TRUST_STATUSES, weights=[0.8, 0.1, 0.03, 0.07])[0],
                        last_seen_at=_random_past_datetime(base_time, 30),
                    )
                )
            )
            device_counter += 1
            link_counter += 1
    return devices, user_devices


def generate_services(config: GeneratorConfig) -> list[dict]:
    services: list[dict] = []
    for idx in range(1, config.num_services + 1):
        sector = random.choice(SECTOR_TYPES)
        services.append(
            asdict(
                ServiceRecord(
                    service_id=f"S{idx:04d}",
                    service_name=f"{sector}_service_{idx:02d}",
                    sector_type=sector,
                    risk_tier=random.choice(RISK_TIERS),
                    supports_myinfo_flag=sector in {"banking", "insurance", "government"},
                    supports_signing_flag=sector in {"banking", "insurance", "government", "other_private"},
                )
            )
        )
    return services
