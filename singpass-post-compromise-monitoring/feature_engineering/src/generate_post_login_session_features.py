from __future__ import annotations

import csv
from collections import Counter, defaultdict, deque
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from statistics import mean


SUCCESSFUL_LOGIN_EVENT_TYPES = {"app_login_success", "qr_login_approved"}
POST_LOGIN_ACTIVITY_CATEGORIES = {
    "service_usage",
    "consent_data_sharing",
    "digital_signing_authorisation",
    "account_device_lifecycle",
}
SENSITIVE_EVENT_TYPES = {
    "consent_request_presented",
    "consent_granted",
    "myinfo_data_access_completed",
    "sign_request_initiated",
    "sign_approved",
    "sign_completed",
    "device_changed",
    "app_reinstalled",
    "contact_detail_updated",
}


@dataclass
class PriorSessionSummary:
    session_start: datetime
    service_id: str
    post_login_event_count: int
    post_login_duration_seconds: int
    sensitive_event_flag: int
    had_consent_flow: int
    had_sign_flow: int


@dataclass
class PriorEventSummary:
    timestamp: datetime
    service_id: str
    event_type: str
    event_category: str


def _parse_dt(value: str) -> datetime:
    return datetime.strptime(value, "%Y-%m-%d %H:%M:%S")


def _parse_bool(value: str) -> int:
    return 1 if str(value).strip().lower() == "true" else 0


def _read_csv(path: Path) -> list[dict]:
    with path.open(newline="") as f:
        return list(csv.DictReader(f))


def _write_csv(rows: list[dict], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        output_path.write_text("")
        return
    with output_path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def _write_text(text: str, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(text)


def _days_between(later: datetime, earlier: datetime | None) -> int | None:
    if earlier is None:
        return None
    return max((later - earlier).days, 0)


def _safe_mean(values: list[int | float]) -> float | None:
    return mean(values) if values else None


def _trim_sessions(history: deque[PriorSessionSummary], threshold: datetime) -> None:
    while history and history[0].session_start < threshold:
        history.popleft()


def _trim_events(history: deque[PriorEventSummary], threshold: datetime) -> None:
    while history and history[0].timestamp < threshold:
        history.popleft()


def _null_rate(rows: list[dict], key: str) -> tuple[int, float]:
    missing = sum(1 for row in rows if row.get(key, "") in {"", None})
    return missing, (missing / len(rows)) if rows else 0.0


def build_post_login_session_features() -> tuple[list[dict], dict]:
    repo_root = Path(__file__).resolve().parents[3]
    generated_dir = repo_root / "data" / "input_data" / "generated"

    sessions = _read_csv(generated_dir / "sessions.csv")
    events = _read_csv(generated_dir / "events.csv")
    labels = _read_csv(generated_dir / "fraud_labels.csv")
    services = _read_csv(generated_dir / "services.csv")
    user_devices = _read_csv(generated_dir / "user_devices.csv")

    service_map = {row["service_id"]: row for row in services}
    user_device_map = {(row["user_id"], row["device_id"]): row for row in user_devices}

    events_by_session: dict[str, list[dict]] = defaultdict(list)
    for event in events:
        events_by_session[event["session_id"]].append(event)

    labels_by_session: dict[str, list[dict]] = defaultdict(list)
    event_to_session = {event["event_id"]: event["session_id"] for event in events}
    for label in labels:
        if label["fraud_stage"] != "post_login_stage":
            continue
        session_id = event_to_session.get(label["event_id"])
        if session_id:
            labels_by_session[session_id].append(label)

    monitored_session_inputs: list[dict] = []

    for session in sessions:
        if _parse_bool(session["authenticated_flag"]) != 1:
            continue

        session_events = sorted(
            events_by_session.get(session["session_id"], []),
            key=lambda row: (_parse_dt(row["event_timestamp"]), row["event_id"]),
        )
        if not session_events:
            continue

        login_event = next((e for e in session_events if e["event_type"] in SUCCESSFUL_LOGIN_EVENT_TYPES), None)
        if login_event is None:
            continue

        login_ts = _parse_dt(login_event["event_timestamp"])
        post_login_events = [
            event
            for event in session_events
            if _parse_dt(event["event_timestamp"]) > login_ts
            and event["event_category"] in POST_LOGIN_ACTIVITY_CATEGORIES
        ]
        if not post_login_events:
            continue

        monitored_session_inputs.append(
            {
                "session": session,
                "login_event": login_event,
                "session_events": session_events,
                "post_login_events": post_login_events,
                "labels": labels_by_session.get(session["session_id"], []),
            }
        )

    monitored_session_inputs.sort(
        key=lambda item: (
            _parse_dt(item["session"]["session_start_at"]),
            item["session"]["session_id"],
        )
    )

    prior_sessions_by_user: dict[str, deque[PriorSessionSummary]] = defaultdict(deque)
    prior_events_by_user: dict[str, deque[PriorEventSummary]] = defaultdict(deque)

    feature_rows: list[dict] = []

    for item in monitored_session_inputs:
        session = item["session"]
        login_event = item["login_event"]
        post_login_events = item["post_login_events"]
        session_labels = item["labels"]

        session_id = session["session_id"]
        user_id = session["user_id"]
        device_id = session["device_id"]
        service_id = session["service_id"]
        session_start = _parse_dt(session["session_start_at"])
        login_ts = _parse_dt(login_event["event_timestamp"])
        session_end = _parse_dt(session["session_end_at"])

        threshold_30d = session_start - timedelta(days=30)
        threshold_7d = session_start - timedelta(days=7)
        _trim_sessions(prior_sessions_by_user[user_id], threshold_30d)
        _trim_events(prior_events_by_user[user_id], threshold_30d)

        service = service_map[service_id]
        user_device = user_device_map.get((user_id, device_id))

        post_login_event_count = len(post_login_events)
        post_login_duration_seconds = max(
            int((_parse_dt(post_login_events[-1]["event_timestamp"]) - login_ts).total_seconds()),
            0,
        )
        distinct_event_type_count = len({event["event_type"] for event in post_login_events})
        distinct_service_count = len({event["service_id"] for event in post_login_events})
        sensitive_events = [event for event in post_login_events if event["event_type"] in SENSITIVE_EVENT_TYPES]
        sensitive_event_count = len(sensitive_events)
        benign_service_usage_count = sum(1 for event in post_login_events if event["event_category"] == "service_usage")

        first_post_login_ts = _parse_dt(post_login_events[0]["event_timestamp"])
        time_to_first_post_login_event_seconds = int((first_post_login_ts - login_ts).total_seconds())
        first_sensitive_ts = _parse_dt(sensitive_events[0]["event_timestamp"]) if sensitive_events else None
        time_to_first_sensitive_event_seconds = (
            int((first_sensitive_ts - login_ts).total_seconds()) if first_sensitive_ts else None
        )

        first_switch_ts = None
        previous_service_id = service_id
        service_switch_count = 0
        had_prior_sensitive = False
        sensitive_event_after_sensitive_event_flag = 0
        post_login_times = [_parse_dt(event["event_timestamp"]) for event in post_login_events]
        for event in post_login_events:
            event_ts = _parse_dt(event["event_timestamp"])
            if event["service_id"] != previous_service_id:
                service_switch_count += 1
                previous_service_id = event["service_id"]
                if first_switch_ts is None:
                    first_switch_ts = event_ts
            if event["event_type"] in SENSITIVE_EVENT_TYPES:
                if had_prior_sensitive:
                    sensitive_event_after_sensitive_event_flag = 1
                had_prior_sensitive = True

        time_to_first_service_switch_seconds = (
            int((first_switch_ts - login_ts).total_seconds()) if first_switch_ts else None
        )

        max_event_burst_5m = 0
        burst_window: deque[datetime] = deque()
        for event_ts in post_login_times:
            while burst_window and (event_ts - burst_window[0]).total_seconds() > 300:
                burst_window.popleft()
            burst_window.append(event_ts)
            max_event_burst_5m = max(max_event_burst_5m, len(burst_window))

        consent_events = [event for event in post_login_events if event["event_category"] == "consent_data_sharing"]
        sign_events = [
            event for event in post_login_events if event["event_category"] == "digital_signing_authorisation"
        ]
        consent_granted_count = sum(1 for event in consent_events if event["event_type"] == "consent_granted")
        sign_completed_count = sum(1 for event in sign_events if event["event_type"] == "sign_completed")

        prior_user_sessions = list(prior_sessions_by_user[user_id])
        prior_user_events = list(prior_events_by_user[user_id])
        prior_user_services_30d = {row.service_id for row in prior_user_sessions}
        prior_user_monitored_session_count_30d = len(prior_user_sessions)
        prior_user_sensitive_session_count_30d = sum(row.sensitive_event_flag for row in prior_user_sessions)
        prior_user_avg_post_login_event_count_30d = _safe_mean(
            [row.post_login_event_count for row in prior_user_sessions]
        )
        prior_user_avg_session_duration_seconds_30d = _safe_mean(
            [row.post_login_duration_seconds for row in prior_user_sessions]
        )
        session_event_count_deviation_from_user_avg = (
            post_login_event_count - prior_user_avg_post_login_event_count_30d
            if prior_user_avg_post_login_event_count_30d is not None
            else None
        )
        session_duration_deviation_from_user_avg = (
            post_login_duration_seconds - prior_user_avg_session_duration_seconds_30d
            if prior_user_avg_session_duration_seconds_30d is not None
            else None
        )
        service_usage_count_by_user_30d = sum(1 for row in prior_user_events if row.service_id == service_id)
        service_used_by_user_last_30d_flag = 1 if service_usage_count_by_user_30d > 0 else 0
        first_time_service_access_in_session_flag = 1 if service_id not in prior_user_services_30d else 0
        rare_service_access_flag = 1 if service_usage_count_by_user_30d <= 1 else 0

        first_time_consent_flow_for_user_flag = (
            1
            if consent_events and not any(row.had_consent_flow for row in prior_user_sessions)
            else 0
        )
        first_time_sign_flow_for_user_flag = (
            1
            if sign_events and not any(row.had_sign_flow for row in prior_user_sessions)
            else 0
        )

        recent_lifecycle_change_before_session_flag = 0
        recent_contact_detail_update_before_session_flag = 0
        recent_app_reinstall_before_session_flag = 0
        for row in prior_user_events:
            if row.timestamp < threshold_7d:
                continue
            if row.event_category == "account_device_lifecycle":
                recent_lifecycle_change_before_session_flag = 1
            if row.event_type == "contact_detail_updated":
                recent_contact_detail_update_before_session_flag = 1
            if row.event_type == "app_reinstalled":
                recent_app_reinstall_before_session_flag = 1

        if user_device:
            linked_at = _parse_dt(user_device["linked_at"])
            last_seen_at = _parse_dt(user_device["last_seen_at"]) if user_device["last_seen_at"] else None
            user_device_link_exists_flag = 1
            is_primary_device_flag = _parse_bool(user_device["is_primary_device_flag"])
            trust_status = user_device["trust_status"] or "unknown"
            days_since_device_linked = _days_between(session_start, linked_at)
            days_since_user_device_last_seen = _days_between(session_start, last_seen_at)
        else:
            user_device_link_exists_flag = 0
            is_primary_device_flag = 0
            trust_status = "unknown"
            days_since_device_linked = None
            days_since_user_device_last_seen = None

        fraud_rows = [row for row in session_labels if str(row["is_fraud_flag"]).lower() == "true"]
        target_post_login_fraud_flag = 1 if fraud_rows else 0
        dominant_fraud_scenario = (
            Counter(row["fraud_scenario"] for row in fraud_rows).most_common(1)[0][0]
            if fraud_rows
            else (session_labels[0]["fraud_scenario"] if session_labels else "unknown")
        )

        feature_rows.append(
            {
                "session_id": session_id,
                "user_id": user_id,
                "device_id": device_id,
                "service_id": service_id,
                "login_event_id": login_event["event_id"],
                "login_timestamp": login_event["event_timestamp"],
                "login_event_type": login_event["event_type"],
                "login_method": session["login_method"] or "unknown",
                "channel": login_event["channel"] or "unknown",
                "login_hour_of_day": login_ts.hour,
                "login_country": login_event["country"] or "unknown",
                "login_region": login_event["region"] or "unknown",
                "login_asn": login_event["asn"] or "unknown",
                "service_sector_type": service["sector_type"] or "unknown",
                "service_risk_tier": service["risk_tier"] or "unknown",
                "service_supports_myinfo_flag": _parse_bool(service["supports_myinfo_flag"]),
                "service_supports_signing_flag": _parse_bool(service["supports_signing_flag"]),
                "post_login_event_count": post_login_event_count,
                "post_login_duration_seconds": post_login_duration_seconds,
                "distinct_event_type_count": distinct_event_type_count,
                "distinct_service_count_in_session": distinct_service_count,
                "sensitive_event_count": sensitive_event_count,
                "benign_service_usage_count": benign_service_usage_count,
                "time_to_first_post_login_event_seconds": time_to_first_post_login_event_seconds,
                "time_to_first_sensitive_event_seconds": (
                    time_to_first_sensitive_event_seconds
                    if time_to_first_sensitive_event_seconds is not None
                    else ""
                ),
                "time_to_first_sensitive_event_missing_flag": (
                    0 if time_to_first_sensitive_event_seconds is not None else 1
                ),
                "time_to_first_service_switch_seconds": (
                    time_to_first_service_switch_seconds if time_to_first_service_switch_seconds is not None else ""
                ),
                "time_to_first_service_switch_missing_flag": (
                    0 if time_to_first_service_switch_seconds is not None else 1
                ),
                "max_event_burst_5m": max_event_burst_5m,
                "service_switch_count": service_switch_count,
                "sensitive_event_after_sensitive_event_flag": sensitive_event_after_sensitive_event_flag,
                "consent_event_count": len(consent_events),
                "consent_granted_count": consent_granted_count,
                "sign_event_count": len(sign_events),
                "sign_completed_count": sign_completed_count,
                "has_any_consent_granted_flag": 1 if consent_granted_count > 0 else 0,
                "has_any_sign_completed_flag": 1 if sign_completed_count > 0 else 0,
                "first_time_consent_flow_for_user_flag": first_time_consent_flow_for_user_flag,
                "first_time_sign_flow_for_user_flag": first_time_sign_flow_for_user_flag,
                "first_time_service_access_in_session_flag": first_time_service_access_in_session_flag,
                "service_used_by_user_last_30d_flag": service_used_by_user_last_30d_flag,
                "service_usage_count_by_user_30d": service_usage_count_by_user_30d,
                "rare_service_access_flag": rare_service_access_flag,
                "high_risk_service_access_flag": 1 if service["risk_tier"] == "high" else 0,
                "user_prior_monitored_session_count_30d": prior_user_monitored_session_count_30d,
                "user_prior_sensitive_session_count_30d": prior_user_sensitive_session_count_30d,
                "user_prior_distinct_services_30d": len(prior_user_services_30d),
                "user_prior_avg_post_login_event_count_30d": (
                    f"{prior_user_avg_post_login_event_count_30d:.2f}"
                    if prior_user_avg_post_login_event_count_30d is not None
                    else ""
                ),
                "user_prior_avg_session_duration_seconds_30d": (
                    f"{prior_user_avg_session_duration_seconds_30d:.2f}"
                    if prior_user_avg_session_duration_seconds_30d is not None
                    else ""
                ),
                "session_event_count_deviation_from_user_avg": (
                    f"{session_event_count_deviation_from_user_avg:.2f}"
                    if session_event_count_deviation_from_user_avg is not None
                    else ""
                ),
                "session_event_count_deviation_missing_flag": (
                    0 if session_event_count_deviation_from_user_avg is not None else 1
                ),
                "session_duration_deviation_from_user_avg": (
                    f"{session_duration_deviation_from_user_avg:.2f}"
                    if session_duration_deviation_from_user_avg is not None
                    else ""
                ),
                "session_duration_deviation_missing_flag": (
                    0 if session_duration_deviation_from_user_avg is not None else 1
                ),
                "user_device_link_exists_flag": user_device_link_exists_flag,
                "is_primary_device_flag": is_primary_device_flag,
                "trust_status": trust_status,
                "days_since_device_linked": days_since_device_linked if days_since_device_linked is not None else "",
                "days_since_user_device_last_seen": (
                    days_since_user_device_last_seen if days_since_user_device_last_seen is not None else ""
                ),
                "recent_lifecycle_change_before_session_flag": recent_lifecycle_change_before_session_flag,
                "recent_contact_detail_update_before_session_flag": recent_contact_detail_update_before_session_flag,
                "recent_app_reinstall_before_session_flag": recent_app_reinstall_before_session_flag,
                "target_post_login_fraud_flag": target_post_login_fraud_flag,
                "dominant_fraud_scenario": dominant_fraud_scenario,
            }
        )

        prior_sessions_by_user[user_id].append(
            PriorSessionSummary(
                session_start=session_start,
                service_id=service_id,
                post_login_event_count=post_login_event_count,
                post_login_duration_seconds=post_login_duration_seconds,
                sensitive_event_flag=1 if sensitive_event_count > 0 else 0,
                had_consent_flow=1 if consent_events else 0,
                had_sign_flow=1 if sign_events else 0,
            )
        )
        for event in post_login_events:
            prior_events_by_user[user_id].append(
                PriorEventSummary(
                    timestamp=_parse_dt(event["event_timestamp"]),
                    service_id=event["service_id"],
                    event_type=event["event_type"],
                    event_category=event["event_category"],
                )
            )

    fraud_rows = sum(int(row["target_post_login_fraud_flag"]) for row in feature_rows)
    metrics = {
        "rows": len(feature_rows),
        "fraud_rows": fraud_rows,
        "non_fraud_rows": len(feature_rows) - fraud_rows,
        "fraud_rate": (fraud_rows / len(feature_rows)) if feature_rows else 0.0,
    }
    return feature_rows, metrics


def build_quality_report(rows: list[dict], metrics: dict) -> str:
    scenario_counts = Counter(row["dominant_fraud_scenario"] for row in rows)
    null_keys = [
        "time_to_first_sensitive_event_seconds",
        "time_to_first_service_switch_seconds",
        "user_prior_avg_post_login_event_count_30d",
        "user_prior_avg_session_duration_seconds_30d",
        "session_event_count_deviation_from_user_avg",
        "session_duration_deviation_from_user_avg",
        "days_since_user_device_last_seen",
    ]

    lines = [
        "# Feature Quality Report",
        "",
        "Last updated: 12 April 2026",
        "",
        "## Dataset summary",
        "",
        f"- rows: {metrics['rows']:,}",
        f"- fraud rows: {metrics['fraud_rows']:,}",
        f"- non-fraud rows: {metrics['non_fraud_rows']:,}",
        f"- fraud rate: {metrics['fraud_rate']:.4f}",
        "",
        "## Scenario distribution",
        "",
    ]
    for scenario, count in sorted(scenario_counts.items()):
        lines.append(f"- `{scenario}`: {count:,}")

    lines.extend(
        [
            "",
            "## Null-rate summary",
            "",
        ]
    )
    for key in null_keys:
        missing, rate = _null_rate(rows, key)
        lines.append(f"- `{key}`: {missing:,} null/blank values ({rate:.2%})")

    lines.extend(
        [
            "",
            "## Inspection summary",
            "",
            "- The current table is session-level and therefore suitable for behavioural monitoring rather than single-event scoring.",
            "- Post-login activity volume, sensitive action counts, and burstiness are now available for downstream rules and ML.",
            "- Historical baseline features are expected to contain meaningful nulls for early observed sessions with limited prior history.",
            "- The next step is to inspect separability and null patterns before building the post-login rule layer.",
        ]
    )

    return "\n".join(lines) + "\n"


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    output_dir = repo_root / "singpass-post-compromise-monitoring" / "feature_engineering" / "generated"
    rows, metrics = build_post_login_session_features()
    _write_csv(rows, output_dir / "post_login_session_features.csv")
    _write_text(build_quality_report(rows, metrics), output_dir / "feature_quality_report.md")


if __name__ == "__main__":
    main()
