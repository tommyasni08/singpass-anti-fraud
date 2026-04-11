from __future__ import annotations

import random
from dataclasses import asdict
from datetime import datetime, timedelta

from .schema import EventRecord, FraudLabelRecord


def _make_network(region: str, unusual: bool = False) -> tuple[str, str, str]:
    if region.startswith("SG_") and not unusual:
        return (
            f"103.{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}",
            random.choice(["AS4788", "AS3758", "AS10091"]),
            "SG",
        )
    foreign = random.choice(
        [
            ("198.51.100.17", "AS13335", "MY", "KUALA_LUMPUR"),
            ("203.0.113.24", "AS4761", "ID", "JAKARTA"),
            ("203.0.113.55", "AS7470", "TH", "BANGKOK"),
        ]
    )
    return foreign[0], foreign[1], foreign[2]


def _append_event(
    events: list[dict],
    event_counter: int,
    *,
    timestamp: datetime,
    category: str,
    event_type: str,
    user_id: str,
    device_id: str | None,
    service_id: str | None,
    session_id: str | None,
    ip_address: str,
    asn: str,
    country: str,
    region: str,
    channel: str,
    event_result: str,
    approval_latency_seconds: float | None = None,
    event_metadata_json: dict | None = None,
) -> tuple[int, str]:
    event_id = f"E{event_counter:08d}"
    events.append(
        asdict(
            EventRecord(
                event_id=event_id,
                event_timestamp=timestamp,
                event_category=category,
                event_type=event_type,
                user_id=user_id,
                device_id=device_id,
                service_id=service_id,
                session_id=session_id,
                ip_address=ip_address,
                asn=asn,
                country=country,
                region=region,
                channel=channel,
                event_result=event_result,
                approval_latency_seconds=approval_latency_seconds,
                event_metadata_json=event_metadata_json or {},
            )
        )
    )
    return event_counter + 1, event_id


def generate_events_and_labels(
    sessions: list[dict],
    session_context: list[dict],
    user_map: dict[str, dict],
) -> tuple[list[dict], list[dict]]:
    events: list[dict] = []
    labels: list[dict] = []
    event_counter = 1
    label_counter = 1

    context_by_session = {row["session_id"]: row for row in session_context}

    for session in sessions:
        ctx = context_by_session[session["session_id"]]
        scenario = ctx["scenario_name"]
        login_stage_suspicious = str(ctx.get("login_stage_suspicious", "False")).lower() == "true"
        user = user_map[session["user_id"]]
        base_region = user["primary_region"]

        unusual_network = scenario in {
            "legitimate_travel_or_device_change_login",
            "social_engineering_or_malicious_approval",
            "repeated_attempts_before_success",
        }
        ip_address, asn, country = _make_network(base_region, unusual=unusual_network)
        region = base_region if country == "SG" else random.choice(["KUALA_LUMPUR", "JAKARTA", "BANGKOK"])

        ts = session["session_start_at"]
        channel = random.choice(["mobile_app", "desktop_web"])
        decisive_event_id: str | None = None
        post_login_event_id: str | None = None

        if scenario == "repeated_attempts_before_success":
            for _ in range(random.randint(2, 4)):
                event_counter, _ = _append_event(
                    events,
                    event_counter,
                    timestamp=ts,
                    category="login_authentication",
                    event_type="qr_login_request",
                    user_id=session["user_id"],
                    device_id=session["device_id"],
                    service_id=session["service_id"],
                    session_id=session["session_id"],
                    ip_address=ip_address,
                    asn=asn,
                    country=country,
                    region=region,
                    channel=channel,
                    event_result="success",
                )
                ts += timedelta(seconds=random.randint(20, 90))
                event_counter, _ = _append_event(
                    events,
                    event_counter,
                    timestamp=ts,
                    category="login_authentication",
                    event_type="qr_login_rejected",
                    user_id=session["user_id"],
                    device_id=session["device_id"],
                    service_id=session["service_id"],
                    session_id=session["session_id"],
                    ip_address=ip_address,
                    asn=asn,
                    country=country,
                    region=region,
                    channel="mobile_app",
                    event_result="rejected",
                )
                ts += timedelta(minutes=random.randint(1, 5))

        event_counter, _ = _append_event(
            events,
            event_counter,
            timestamp=ts,
            category="login_authentication",
            event_type="qr_login_request" if session["login_method"] == "qr_login" else "app_login_request",
            user_id=session["user_id"],
            device_id=session["device_id"],
            service_id=session["service_id"],
            session_id=session["session_id"],
            ip_address=ip_address,
            asn=asn,
            country=country,
            region=region,
            channel=channel,
            event_result="success",
        )
        ts += timedelta(seconds=random.randint(5, 40))

        if scenario in {
            "social_engineering_or_malicious_approval",
            "remote_control_or_device_compromise_access",
            "repeated_attempts_before_success",
        }:
            latency = random.choice([1.0, 1.2, 1.5, 2.0])
        else:
            latency = round(random.uniform(4.0, 18.0), 1)

        if session["login_method"] == "qr_login":
            event_counter, _ = _append_event(
                events,
                event_counter,
                timestamp=ts,
                category="login_authentication",
                event_type="qr_login_approval_prompt",
                user_id=session["user_id"],
                device_id=session["device_id"],
                service_id=session["service_id"],
                session_id=session["session_id"],
                ip_address=ip_address,
                asn=asn,
                country=country,
                region=region,
                channel="mobile_app",
                event_result="success",
            )
            ts += timedelta(seconds=max(int(latency), 1))
            event_counter, decisive_event_id = _append_event(
                events,
                event_counter,
                timestamp=ts,
                category="login_authentication",
                event_type="qr_login_approved" if session["authenticated_flag"] else "qr_login_rejected",
                user_id=session["user_id"],
                device_id=session["device_id"],
                service_id=session["service_id"],
                session_id=session["session_id"],
                ip_address=ip_address,
                asn=asn,
                country=country,
                region=region,
                channel="mobile_app",
                event_result="success" if session["authenticated_flag"] else "rejected",
                approval_latency_seconds=latency,
                event_metadata_json={"scenario_name": scenario},
            )
        else:
            event_counter, decisive_event_id = _append_event(
                events,
                event_counter,
                timestamp=ts,
                category="login_authentication",
                event_type="app_login_success" if session["authenticated_flag"] else "app_login_failure",
                user_id=session["user_id"],
                device_id=session["device_id"],
                service_id=session["service_id"],
                session_id=session["session_id"],
                ip_address=ip_address,
                asn=asn,
                country=country,
                region=region,
                channel="mobile_app",
                event_result="success" if session["authenticated_flag"] else "failure",
                approval_latency_seconds=latency,
                event_metadata_json={"scenario_name": scenario},
            )

        ts += timedelta(minutes=random.randint(1, 8))
        if scenario in {
            "legitimate_travel_or_device_change_login",
            "remote_control_or_device_compromise_access",
            "relinquished_account_access_and_operation",
        }:
            event_counter, _ = _append_event(
                events,
                event_counter,
                timestamp=ts,
                category="account_device_lifecycle",
                event_type=random.choice(["device_changed", "app_reinstalled", "contact_detail_updated"]),
                user_id=session["user_id"],
                device_id=session["device_id"],
                service_id=None,
                session_id=session["session_id"],
                ip_address=ip_address,
                asn=asn,
                country=country,
                region=region,
                channel="mobile_app",
                event_result="completed",
                event_metadata_json={"scenario_name": scenario},
            )
            ts += timedelta(minutes=1)

        post_login_category = None
        post_login_type = None
        if session["authenticated_flag"]:
            if scenario in {
                "normal_returning_login_and_normal_usage",
                "legitimate_travel_or_device_change_login",
                "legitimate_first_time_or_infrequent_service_usage",
            }:
                post_login_category = "service_usage"
                post_login_type = random.choice(
                    ["service_access_view", "dashboard_view", "profile_view", "history_view"]
                )
            elif scenario in {
                "social_engineering_or_malicious_approval",
                "relinquished_account_access_and_operation",
                "suspicious_downstream_misuse_after_successful_access",
            }:
                if random.random() < 0.5:
                    post_login_category = "consent_data_sharing"
                    post_login_type = random.choice(
                        ["consent_request_presented", "consent_granted", "myinfo_data_access_completed"]
                    )
                else:
                    post_login_category = "digital_signing_authorisation"
                    post_login_type = random.choice(
                        ["sign_request_initiated", "sign_approved", "sign_completed"]
                    )
            elif scenario == "remote_control_or_device_compromise_access":
                post_login_category = "service_usage"
                post_login_type = random.choice(
                    ["service_access_view", "dashboard_view", "profile_view"]
                )

        if post_login_category and post_login_type and session["authenticated_flag"]:
            if post_login_category == "consent_data_sharing":
                event_counter, post_login_event_id = _append_event(
                    events,
                    event_counter,
                    timestamp=ts,
                    category=post_login_category,
                    event_type=post_login_type,
                    user_id=session["user_id"],
                    device_id=session["device_id"],
                    service_id=session["service_id"],
                    session_id=session["session_id"],
                    ip_address=ip_address,
                    asn=asn,
                    country=country,
                    region=region,
                    channel="mobile_app",
                    event_result="completed",
                    event_metadata_json={"scenario_name": scenario},
                )
            elif post_login_category == "digital_signing_authorisation":
                event_counter, post_login_event_id = _append_event(
                    events,
                    event_counter,
                    timestamp=ts,
                    category=post_login_category,
                    event_type=post_login_type,
                    user_id=session["user_id"],
                    device_id=session["device_id"],
                    service_id=session["service_id"],
                    session_id=session["session_id"],
                    ip_address=ip_address,
                    asn=asn,
                    country=country,
                    region=region,
                    channel="mobile_app",
                    event_result="completed",
                    event_metadata_json={"scenario_name": scenario},
                )
            else:
                event_counter, post_login_event_id = _append_event(
                    events,
                    event_counter,
                    timestamp=ts,
                    category=post_login_category,
                    event_type=post_login_type,
                    user_id=session["user_id"],
                    device_id=session["device_id"],
                    service_id=session["service_id"],
                    session_id=session["session_id"],
                    ip_address=ip_address,
                    asn=asn,
                    country=country,
                    region=region,
                    channel="mobile_app",
                    event_result="completed",
                    event_metadata_json={"scenario_name": scenario},
                )

        if decisive_event_id:
            is_login_fraud = scenario in {
                "remote_control_or_device_compromise_access",
                "repeated_attempts_before_success",
            } or (
                scenario in {
                    "social_engineering_or_malicious_approval",
                    "relinquished_account_access_and_operation",
                }
                and login_stage_suspicious
            )
            labels.append(
                asdict(
                    FraudLabelRecord(
                        label_id=f"L{label_counter:06d}",
                        event_id=decisive_event_id,
                        user_id=session["user_id"],
                        label_timestamp=session["session_end_at"],
                        is_fraud_flag=is_login_fraud,
                        fraud_scenario=scenario,
                        fraud_stage="login_stage",
                        downstream_damage_flag=is_login_fraud and scenario == "relinquished_account_access_and_operation",
                    )
                )
            )
            label_counter += 1

        if scenario in {
            "legitimate_first_time_or_infrequent_service_usage",
            "normal_returning_login_and_normal_usage",
            "legitimate_travel_or_device_change_login",
            "suspicious_downstream_misuse_after_successful_access",
            "relinquished_account_access_and_operation",
            "social_engineering_or_malicious_approval",
            "remote_control_or_device_compromise_access",
        } and post_login_event_id:
            labels.append(
                asdict(
                    FraudLabelRecord(
                        label_id=f"L{label_counter:06d}",
                        event_id=post_login_event_id,
                        user_id=session["user_id"],
                        label_timestamp=session["session_end_at"],
                        is_fraud_flag=scenario not in {
                            "legitimate_first_time_or_infrequent_service_usage",
                            "normal_returning_login_and_normal_usage",
                            "legitimate_travel_or_device_change_login",
                        },
                        fraud_scenario=scenario,
                        fraud_stage="post_login_stage",
                        downstream_damage_flag=scenario in {
                            "suspicious_downstream_misuse_after_successful_access",
                            "relinquished_account_access_and_operation",
                        },
                    )
                )
            )
            label_counter += 1

    return events, labels
