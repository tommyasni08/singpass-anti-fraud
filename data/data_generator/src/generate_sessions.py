from __future__ import annotations

import random
from dataclasses import asdict
from datetime import datetime, timedelta

from .config import GeneratorConfig
from .constants import LOGIN_METHODS
from .schema import SessionRecord


def _sample_session_count(avg_sessions_per_user: int) -> int:
    low = max(1, avg_sessions_per_user - 4)
    high = max(low, avg_sessions_per_user + 4)
    return random.randint(low, high)


def _choose_scenario(scenario_weights: dict[str, float]) -> str:
    names = list(scenario_weights.keys())
    weights = list(scenario_weights.values())
    return random.choices(names, weights=weights, k=1)[0]


def _choose_login_method(scenario_name: str) -> str:
    if scenario_name in {
        "social_engineering_or_malicious_approval",
        "repeated_attempts_before_success",
    }:
        return random.choices(["qr_login", "app_login"], weights=[0.7, 0.3])[0]
    if scenario_name == "remote_control_or_device_compromise_access":
        return random.choices(["app_login", "qr_login", "face_verification"], weights=[0.6, 0.25, 0.15])[0]
    return random.choices(LOGIN_METHODS, weights=[0.55, 0.35, 0.10])[0]


def _choose_session_status(scenario_name: str) -> tuple[str, bool]:
    if scenario_name in {
        "normal_returning_login_and_normal_usage",
        "legitimate_travel_or_device_change_login",
        "legitimate_first_time_or_infrequent_service_usage",
        "social_engineering_or_malicious_approval",
        "remote_control_or_device_compromise_access",
        "relinquished_account_access_and_operation",
        "suspicious_downstream_misuse_after_successful_access",
    }:
        return "completed", True
    if scenario_name == "repeated_attempts_before_success":
        return random.choices(
            [("completed", True), ("failed", False), ("abandoned", False)],
            weights=[0.6, 0.25, 0.15],
            k=1,
        )[0]
    return "completed", True


def _login_stage_suspicious_flag(scenario_name: str) -> bool:
    if scenario_name == "social_engineering_or_malicious_approval":
        return random.random() < 0.65
    if scenario_name == "relinquished_account_access_and_operation":
        return random.random() < 0.35
    if scenario_name == "remote_control_or_device_compromise_access":
        return True
    if scenario_name == "repeated_attempts_before_success":
        return True
    return False


def generate_sessions(
    config: GeneratorConfig,
    users: list[dict],
    user_devices: list[dict],
    services: list[dict],
    base_time: datetime,
) -> tuple[list[dict], list[dict]]:
    sessions: list[dict] = []
    session_context: list[dict] = []

    devices_by_user: dict[str, list[dict]] = {}
    for row in user_devices:
        devices_by_user.setdefault(row["user_id"], []).append(row)

    session_counter = 1

    for user in users:
        user_id = user["user_id"]
        linked_devices = devices_by_user.get(user_id, [])
        if not linked_devices:
            continue

        num_sessions = _sample_session_count(config.avg_sessions_per_user)
        for _ in range(num_sessions):
            scenario_name = _choose_scenario(config.scenario_weights)
            device_link = random.choice(linked_devices)
            service = random.choice(services)

            session_end_at = base_time - timedelta(
                days=random.randint(0, 180),
                hours=random.randint(0, 23),
                minutes=random.randint(0, 59),
            )
            duration_minutes = random.randint(1, 45)
            session_start_at = session_end_at - timedelta(minutes=duration_minutes)
            session_status, authenticated_flag = _choose_session_status(scenario_name)
            login_method = _choose_login_method(scenario_name)

            session_id = f"SE{session_counter:06d}"
            sessions.append(
                asdict(
                    SessionRecord(
                        session_id=session_id,
                        user_id=user_id,
                        device_id=device_link["device_id"],
                        service_id=service["service_id"],
                        session_start_at=session_start_at,
                        session_end_at=session_end_at,
                        session_status=session_status,
                        login_method=login_method,
                        authenticated_flag=authenticated_flag,
                    )
                )
            )
            session_context.append(
                {
                    "session_id": session_id,
                    "scenario_name": scenario_name,
                    "user_id": user_id,
                    "device_id": device_link["device_id"],
                    "service_id": service["service_id"],
                    "authenticated_flag": authenticated_flag,
                    "login_stage_suspicious": _login_stage_suspicious_flag(scenario_name),
                }
            )
            session_counter += 1

    return sessions, session_context
