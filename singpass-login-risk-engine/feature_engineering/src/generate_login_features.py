from __future__ import annotations

import csv
from collections import Counter, defaultdict, deque
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from statistics import mean, median


SCORED_LOGIN_EVENT_TYPES = {"app_login_success", "qr_login_approved"}
DECISIVE_LOGIN_EVENT_TYPES = {
    "app_login_success",
    "app_login_failure",
    "qr_login_approved",
    "qr_login_rejected",
}
FAILED_LOGIN_EVENT_TYPES = {"app_login_failure"}
REJECTED_LOGIN_EVENT_TYPES = {"qr_login_rejected"}


@dataclass
class HistoryEvent:
    timestamp: datetime
    service_id: str
    country: str
    region: str
    asn: str
    user_id: str


def _parse_bool(value: str) -> int:
    return 1 if str(value).strip().lower() == "true" else 0


def _parse_dt(value: str) -> datetime:
    return datetime.strptime(value, "%Y-%m-%d %H:%M:%S")


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


def _days_between(later: datetime, earlier: datetime) -> int:
    return max((later - earlier).days, 0)


def _iso(ts: datetime | None) -> str:
    return ts.strftime("%Y-%m-%d %H:%M:%S") if ts else ""


def _build_user_device_index(user_devices: list[dict]) -> dict[tuple[str, str], dict]:
    index: dict[tuple[str, str], dict] = {}
    for row in user_devices:
        index[(row["user_id"], row["device_id"])] = row
    return index


def _build_login_labels(labels: list[dict]) -> dict[str, dict]:
    return {
        row["event_id"]: row
        for row in labels
        if row["fraud_stage"] == "login_stage"
    }


def _build_session_precursor_features(events_by_session: dict[str, list[dict]]) -> dict[str, dict]:
    features_by_event_id: dict[str, dict] = {}

    for session_id, session_events in events_by_session.items():
        sorted_events = sorted(session_events, key=lambda row: _parse_dt(row["event_timestamp"]))
        event_count = 0
        failed_count = 0
        rejected_count = 0
        qr_request_count = 0
        qr_prompt_count = 0
        lifecycle_count = 0
        contact_update_count = 0

        for event in sorted_events:
            event_type = event["event_type"]
            event_id = event["event_id"]

            if event_type in SCORED_LOGIN_EVENT_TYPES:
                features_by_event_id[event_id] = {
                    "session_event_count_before_login": event_count,
                    "session_failed_login_events_before_login": failed_count,
                    "session_rejected_login_events_before_login": rejected_count,
                    "session_qr_request_count_before_login": qr_request_count,
                    "session_qr_prompt_count_before_login": qr_prompt_count,
                    "session_has_lifecycle_event_before_login_flag": 1 if lifecycle_count > 0 else 0,
                    "session_lifecycle_event_count_before_login": lifecycle_count,
                    "session_has_contact_detail_updated_before_login_flag": 1 if contact_update_count > 0 else 0,
                }

            event_count += 1

            if event_type in FAILED_LOGIN_EVENT_TYPES:
                failed_count += 1
            if event_type in REJECTED_LOGIN_EVENT_TYPES:
                rejected_count += 1
            if event_type == "qr_login_request":
                qr_request_count += 1
            if event_type == "qr_login_approval_prompt":
                qr_prompt_count += 1
            if event["event_category"] == "account_device_lifecycle":
                lifecycle_count += 1
            if event_type == "contact_detail_updated":
                contact_update_count += 1

    return features_by_event_id


def _trim_window(history: deque[HistoryEvent], threshold: datetime) -> None:
    while history and history[0].timestamp < threshold:
        history.popleft()


def _history_counts(history: deque[HistoryEvent]) -> tuple[int, set[str], set[str], set[str], set[str]]:
    services = {row.service_id for row in history}
    countries = {row.country for row in history}
    regions = {row.region for row in history}
    asns = {row.asn for row in history}
    users = {row.user_id for row in history}
    return len(history), services, countries, regions, asns, users


def build_login_features() -> tuple[list[dict], dict]:
    repo_root = Path(__file__).resolve().parents[3]
    generated_dir = repo_root / "data" / "input_data" / "generated"

    sessions = _read_csv(generated_dir / "sessions.csv")
    events = _read_csv(generated_dir / "events.csv")
    labels = _read_csv(generated_dir / "fraud_labels.csv")
    services = _read_csv(generated_dir / "services.csv")
    user_devices = _read_csv(generated_dir / "user_devices.csv")

    session_map = {row["session_id"]: row for row in sessions}
    service_map = {row["service_id"]: row for row in services}
    user_device_map = _build_user_device_index(user_devices)
    login_label_map = _build_login_labels(labels)

    events_by_session: dict[str, list[dict]] = defaultdict(list)
    for row in events:
        events_by_session[row["session_id"]].append(row)

    session_precursor_map = _build_session_precursor_features(events_by_session)

    sorted_events = sorted(events, key=lambda row: (_parse_dt(row["event_timestamp"]), row["event_id"]))

    user_all_login_7d: dict[str, deque[HistoryEvent]] = defaultdict(deque)
    user_success_login_7d: dict[str, deque[HistoryEvent]] = defaultdict(deque)
    user_rejected_login_7d: dict[str, deque[HistoryEvent]] = defaultdict(deque)
    user_success_login_30d: dict[str, deque[HistoryEvent]] = defaultdict(deque)
    device_success_login_30d: dict[str, deque[HistoryEvent]] = defaultdict(deque)
    user_last_success_at: dict[str, datetime] = {}

    feature_rows: list[dict] = []

    for event in sorted_events:
        event_type = event["event_type"]
        event_ts = _parse_dt(event["event_timestamp"])
        user_id = event["user_id"]
        device_id = event["device_id"]
        service_id = event["service_id"]

        if event_type in SCORED_LOGIN_EVENT_TYPES:
            label = login_label_map.get(event["event_id"])
            if label is None:
                continue

            session = session_map[event["session_id"]]
            service = service_map[service_id]
            user_device = user_device_map.get((user_id, device_id))

            threshold_7d = event_ts - timedelta(days=7)
            threshold_30d = event_ts - timedelta(days=30)

            _trim_window(user_all_login_7d[user_id], threshold_7d)
            _trim_window(user_success_login_7d[user_id], threshold_7d)
            _trim_window(user_rejected_login_7d[user_id], threshold_7d)
            _trim_window(user_success_login_30d[user_id], threshold_30d)
            _trim_window(device_success_login_30d[device_id], threshold_30d)

            prior_login_count_7d, _, _, _, _, _ = _history_counts(user_all_login_7d[user_id])
            prior_success_count_7d, _, _, _, _, _ = _history_counts(user_success_login_7d[user_id])
            prior_rejected_count_7d, _, _, _, _, _ = _history_counts(user_rejected_login_7d[user_id])
            _, prior_services_30d, prior_countries_30d, prior_regions_30d, prior_asns_30d, _ = _history_counts(
                user_success_login_30d[user_id]
            )
            _, _, _, _, _, device_users_30d = _history_counts(device_success_login_30d[device_id])

            prior_service_used_flag = 1 if service_id in prior_services_30d else 0
            approval_latency_missing = 1 if not event["approval_latency_seconds"] else 0

            if user_device:
                linked_at = _parse_dt(user_device["linked_at"])
                last_seen_at = _parse_dt(user_device["last_seen_at"]) if user_device["last_seen_at"] else None
                days_since_device_linked = _days_between(event_ts, linked_at)
                days_since_user_device_last_seen = (
                    _days_between(event_ts, last_seen_at) if last_seen_at else None
                )
                trust_status = user_device["trust_status"] or "unknown"
                user_device_link_exists_flag = 1
                is_primary_device_flag = _parse_bool(user_device["is_primary_device_flag"])
            else:
                days_since_device_linked = None
                days_since_user_device_last_seen = None
                trust_status = "unknown"
                user_device_link_exists_flag = 0
                is_primary_device_flag = 0

            last_success_at = user_last_success_at.get(user_id)
            days_since_last_successful_login = (
                _days_between(event_ts, last_success_at) if last_success_at else None
            )

            precursor = session_precursor_map.get(event["event_id"], {})

            feature_rows.append(
                {
                    "event_id": event["event_id"],
                    "session_id": event["session_id"],
                    "user_id": user_id,
                    "device_id": device_id,
                    "service_id": service_id,
                    "event_timestamp": event["event_timestamp"],
                    "login_event_type": event_type,
                    "login_method": session["login_method"] or "unknown",
                    "channel": event["channel"] or "unknown",
                    "event_result": event["event_result"] or "unknown",
                    "approval_latency_seconds": event["approval_latency_seconds"] or "",
                    "approval_latency_missing_flag": approval_latency_missing,
                    "login_hour_of_day": event_ts.hour,
                    "service_sector_type": service["sector_type"] or "unknown",
                    "service_risk_tier": service["risk_tier"] or "unknown",
                    "service_supports_myinfo_flag": _parse_bool(service["supports_myinfo_flag"]),
                    "service_supports_signing_flag": _parse_bool(service["supports_signing_flag"]),
                    "user_device_link_exists_flag": user_device_link_exists_flag,
                    "is_primary_device_flag": is_primary_device_flag,
                    "trust_status": trust_status,
                    "days_since_device_linked": days_since_device_linked if days_since_device_linked is not None else "",
                    "days_since_user_device_last_seen": (
                        days_since_user_device_last_seen if days_since_user_device_last_seen is not None else ""
                    ),
                    "country": event["country"] or "unknown",
                    "region": event["region"] or "unknown",
                    "asn": event["asn"] or "unknown",
                    "ip_address": event["ip_address"],
                    "new_country_for_user_flag": 1 if event["country"] not in prior_countries_30d else 0,
                    "new_region_for_user_flag": 1 if event["region"] not in prior_regions_30d else 0,
                    "new_asn_for_user_flag": 1 if event["asn"] not in prior_asns_30d else 0,
                    "session_event_count_before_login": precursor.get("session_event_count_before_login", 0),
                    "session_failed_login_events_before_login": precursor.get(
                        "session_failed_login_events_before_login", 0
                    ),
                    "session_rejected_login_events_before_login": precursor.get(
                        "session_rejected_login_events_before_login", 0
                    ),
                    "session_qr_request_count_before_login": precursor.get("session_qr_request_count_before_login", 0),
                    "session_qr_prompt_count_before_login": precursor.get("session_qr_prompt_count_before_login", 0),
                    "session_has_lifecycle_event_before_login_flag": precursor.get(
                        "session_has_lifecycle_event_before_login_flag", 0
                    ),
                    "session_lifecycle_event_count_before_login": precursor.get(
                        "session_lifecycle_event_count_before_login", 0
                    ),
                    "session_has_contact_detail_updated_before_login_flag": precursor.get(
                        "session_has_contact_detail_updated_before_login_flag", 0
                    ),
                    "user_prior_login_count_7d": prior_login_count_7d,
                    "user_prior_successful_login_count_7d": prior_success_count_7d,
                    "user_prior_rejected_login_count_7d": prior_rejected_count_7d,
                    "user_prior_distinct_services_30d": len(prior_services_30d),
                    "user_prior_distinct_countries_30d": len(prior_countries_30d),
                    "user_prior_distinct_asns_30d": len(prior_asns_30d),
                    "days_since_last_successful_login": (
                        days_since_last_successful_login if days_since_last_successful_login is not None else ""
                    ),
                    "days_since_last_successful_login_missing_flag": 1 if last_success_at is None else 0,
                    "device_prior_login_count_30d": len(device_success_login_30d[device_id]),
                    "device_prior_distinct_users_30d": len(device_users_30d),
                    "device_used_by_multiple_users_flag": 1 if len(device_users_30d) > 1 else 0,
                    "first_time_service_for_user_flag": 0 if prior_service_used_flag else 1,
                    "service_used_by_user_last_30d_flag": prior_service_used_flag,
                    "service_usage_count_by_user_30d": sum(
                        1 for item in user_success_login_30d[user_id] if item.service_id == service_id
                    ),
                    "target_login_fraud_flag": _parse_bool(label["is_fraud_flag"]),
                    "fraud_scenario": label["fraud_scenario"],
                }
            )

        if event_type in DECISIVE_LOGIN_EVENT_TYPES:
            history_event = HistoryEvent(
                timestamp=event_ts,
                service_id=service_id,
                country=event["country"],
                region=event["region"],
                asn=event["asn"],
                user_id=user_id,
            )
            user_all_login_7d[user_id].append(history_event)

            if event_type in SCORED_LOGIN_EVENT_TYPES:
                user_success_login_7d[user_id].append(history_event)
                user_success_login_30d[user_id].append(history_event)
                device_success_login_30d[device_id].append(history_event)
                user_last_success_at[user_id] = event_ts
            elif event_type in FAILED_LOGIN_EVENT_TYPES or event_type in REJECTED_LOGIN_EVENT_TYPES:
                user_rejected_login_7d[user_id].append(history_event)

    summary = {
        "row_count": len(feature_rows),
        "fraud_count": sum(int(row["target_login_fraud_flag"]) for row in feature_rows),
        "non_fraud_count": sum(1 - int(row["target_login_fraud_flag"]) for row in feature_rows),
        "event_type_counts": Counter(row["login_event_type"] for row in feature_rows),
        "scenario_counts": Counter(row["fraud_scenario"] for row in feature_rows),
    }
    return feature_rows, summary


def _build_quality_report(rows: list[dict], summary: dict) -> str:
    row_count = summary["row_count"]
    fraud_count = summary["fraud_count"]
    non_fraud_count = summary["non_fraud_count"]
    fraud_rate = (fraud_count / row_count) if row_count else 0.0

    null_lines = []
    for column in rows[0].keys():
        null_count = sum(1 for row in rows if row[column] in {"", None})
        null_rate = (null_count / row_count) if row_count else 0.0
        null_lines.append((column, null_count, null_rate))

    null_lines.sort(key=lambda item: (-item[1], item[0]))

    def _group_rows(flag: str) -> list[dict]:
        return [row for row in rows if str(row["target_login_fraud_flag"]) == flag]

    fraud_rows = _group_rows("1")
    non_fraud_rows = _group_rows("0")

    def _numeric_series(subset: list[dict], column: str) -> list[float]:
        values = []
        for row in subset:
            value = row[column]
            if value in {"", None}:
                continue
            values.append(float(value))
        return values

    def _rate(subset: list[dict], column: str, positive_value: str = "1") -> float:
        if not subset:
            return 0.0
        return sum(1 for row in subset if str(row[column]) == positive_value) / len(subset)

    def _top_categories(subset: list[dict], column: str, top_n: int = 4) -> list[tuple[str, int, float]]:
        if not subset:
            return []
        counts = Counter(row[column] for row in subset)
        total = len(subset)
        return [(value, count, count / total) for value, count in counts.most_common(top_n)]

    inspection_numeric_features = [
        "approval_latency_seconds",
        "session_rejected_login_events_before_login",
        "session_qr_request_count_before_login",
        "user_prior_login_count_7d",
        "user_prior_rejected_login_count_7d",
        "device_prior_login_count_30d",
        "service_usage_count_by_user_30d",
    ]
    inspection_boolean_features = [
        "new_country_for_user_flag",
        "new_region_for_user_flag",
        "new_asn_for_user_flag",
        "user_device_link_exists_flag",
        "first_time_service_for_user_flag",
        "device_used_by_multiple_users_flag",
        "days_since_last_successful_login_missing_flag",
    ]
    inspection_categorical_features = [
        "login_event_type",
        "login_method",
        "service_risk_tier",
        "trust_status",
        "country",
    ]

    report = [
        "# Feature Quality Report",
        "",
        "Last updated: 11 April 2026",
        "",
        "## Dataset summary",
        "",
        f"- rows: {row_count:,}",
        f"- fraud rows: {fraud_count:,}",
        f"- non-fraud rows: {non_fraud_count:,}",
        f"- fraud rate: {fraud_rate:.4f}",
        "",
        "## Scored login event types",
        "",
    ]

    for event_type, count in sorted(summary["event_type_counts"].items()):
        report.append(f"- `{event_type}`: {count:,}")

    report.extend(["", "## Scenario distribution", ""])
    for scenario, count in sorted(summary["scenario_counts"].items()):
        report.append(f"- `{scenario}`: {count:,}")

    report.extend(["", "## Null-rate summary", ""])
    for column, null_count, null_rate in null_lines:
        report.append(f"- `{column}`: {null_count:,} null/blank values ({null_rate:.2%})")

    report.extend(["", "## Inspection summary", ""])
    report.extend(
        [
            "- The current feature table is sufficient to proceed to a first hybrid baseline.",
            "- There is already clear separation signal for both rules and ML in latency, repeated-attempt context, and novelty-style features.",
            "- The current weak area is lifecycle-related precursor context, which is sparse because the generator mostly emits lifecycle events after login.",
        ]
    )

    report.extend(["", "## Numeric feature inspection", ""])
    for column in inspection_numeric_features:
        fraud_values = _numeric_series(fraud_rows, column)
        non_fraud_values = _numeric_series(non_fraud_rows, column)
        if not fraud_values and not non_fraud_values:
            continue
        report.append(f"- `{column}`")
        report.append(
            f"  fraud mean/median: {mean(fraud_values):.2f} / {median(fraud_values):.2f}"
            if fraud_values
            else "  fraud mean/median: n/a"
        )
        report.append(
            f"  non-fraud mean/median: {mean(non_fraud_values):.2f} / {median(non_fraud_values):.2f}"
            if non_fraud_values
            else "  non-fraud mean/median: n/a"
        )

    report.extend(["", "## Boolean feature inspection", ""])
    for column in inspection_boolean_features:
        fraud_rate_col = _rate(fraud_rows, column)
        non_fraud_rate_col = _rate(non_fraud_rows, column)
        report.append(
            f"- `{column}`: fraud positive rate {fraud_rate_col:.2%}, non-fraud positive rate {non_fraud_rate_col:.2%}"
        )

    report.extend(["", "## Categorical feature inspection", ""])
    for column in inspection_categorical_features:
        report.append(f"- `{column}`")
        fraud_top = _top_categories(fraud_rows, column)
        non_fraud_top = _top_categories(non_fraud_rows, column)
        fraud_render = ", ".join(f"{value} ({rate:.1%})" for value, _, rate in fraud_top) or "n/a"
        non_fraud_render = ", ".join(f"{value} ({rate:.1%})" for value, _, rate in non_fraud_top) or "n/a"
        report.append(f"  fraud top values: {fraud_render}")
        report.append(f"  non-fraud top values: {non_fraud_render}")

    report.extend(["", "## Hybrid baseline assessment", ""])
    report.extend(
        [
            "- Rule-ready features already exist for repeated-attempt patterns through `session_rejected_login_events_before_login` and `session_qr_request_count_before_login`.",
            "- Rule-ready features also exist for suspiciously fast approvals through `approval_latency_seconds`.",
            "- ML-ready contextual variation exists in service sensitivity, trust status, novelty flags, and short-window history counts.",
            "- The current table is strong enough for a first rule baseline and a simple tree-based model.",
            "- Additional feature passes are still useful later, but they are not required before the first baseline.",
        ]
    )

    report.extend(
        [
            "",
            "## Notes",
            "",
            "- Null and blank values are expected for some time-delta or relationship-derived features.",
            "- This first pass uses only information available at or before the decisive login event timestamp.",
            "- Lifecycle-related precursor features are expected to be sparse in version 1 because the current generator mostly emits lifecycle events after login success.",
        ]
    )

    return "\n".join(report) + "\n"


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    feature_dir = repo_root / "singpass-login-risk-engine" / "feature_engineering"
    output_dir = feature_dir / "generated"

    rows, summary = build_login_features()
    _write_csv(rows, output_dir / "login_features.csv")
    _write_text(_build_quality_report(rows, summary), output_dir / "feature_quality_report.md")

    print(f"Generated login features in {output_dir}")


if __name__ == "__main__":
    main()
