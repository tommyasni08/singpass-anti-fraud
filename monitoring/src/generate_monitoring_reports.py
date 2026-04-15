from __future__ import annotations

import csv
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = REPO_ROOT / "monitoring" / "generated"


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


def _write_json(data: dict, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(data, indent=2) + "\n")


def _pct(numerator: int, denominator: int) -> str:
    if denominator == 0:
        return "0.00%"
    return f"{(numerator / denominator):.2%}"


def _score_band(score: float, thresholds: tuple[float, float]) -> str:
    low_upper, medium_upper = thresholds
    if score < low_upper:
        return "low"
    if score < medium_upper:
        return "medium"
    return "high"


def _null_rate(rows: list[dict], key: str) -> tuple[int, str]:
    missing = sum(1 for row in rows if row.get(key, "") in {"", None})
    return missing, _pct(missing, len(rows))


def build_login_monitoring() -> tuple[list[dict], dict]:
    hybrid_rows = _read_csv(
        REPO_ROOT / "singpass-login-risk-engine" / "hybrid_score" / "generated" / "hybrid_scores.csv"
    )
    feature_rows = _read_csv(
        REPO_ROOT / "singpass-login-risk-engine" / "feature_engineering" / "generated" / "login_features.csv"
    )

    total_rows = len(hybrid_rows)
    fraud_rows = sum(1 for row in hybrid_rows if row["target_login_fraud_flag"] == "1")
    review_rows = sum(1 for row in hybrid_rows if row["hybrid_review_flag"] == "1")
    review_fraud_rows = sum(
        1 for row in hybrid_rows if row["hybrid_review_flag"] == "1" and row["target_login_fraud_flag"] == "1"
    )

    action_counter = Counter(row["hybrid_action"] for row in hybrid_rows)
    action_fraud_counter = Counter(
        row["hybrid_action"] for row in hybrid_rows if row["target_login_fraud_flag"] == "1"
    )
    band_counter = Counter(_score_band(float(row["ml_score"]), (0.3, 0.8)) for row in hybrid_rows)

    summary_rows = []
    for action in sorted(action_counter):
        total = action_counter[action]
        fraud = action_fraud_counter[action]
        summary_rows.append(
            {
                "scoring_name": "login_score",
                "metric_group": "action_distribution",
                "metric_key": action,
                "metric_value": total,
                "metric_rate": _pct(total, total_rows),
                "fraud_rows": fraud,
                "fraud_rate_within_group": _pct(fraud, total),
            }
        )

    for band in ["low", "medium", "high"]:
        total = band_counter[band]
        summary_rows.append(
            {
                "scoring_name": "login_score",
                "metric_group": "ml_score_band",
                "metric_key": band,
                "metric_value": total,
                "metric_rate": _pct(total, total_rows),
                "fraud_rows": "",
                "fraud_rate_within_group": "",
            }
        )

    approval_missing, approval_missing_rate = _null_rate(feature_rows, "approval_latency_seconds")
    last_success_missing, last_success_missing_rate = _null_rate(feature_rows, "days_since_last_successful_login")

    summary = {
        "total_rows": total_rows,
        "fraud_rows": fraud_rows,
        "review_rows": review_rows,
        "review_rate": _pct(review_rows, total_rows),
        "recall": _pct(review_fraud_rows, fraud_rows),
        "precision": _pct(review_fraud_rows, review_rows),
        "approval_latency_missing_rows": approval_missing,
        "approval_latency_missing_rate": approval_missing_rate,
        "days_since_last_success_missing_rows": last_success_missing,
        "days_since_last_success_missing_rate": last_success_missing_rate,
    }
    return summary_rows, summary


def build_session_monitoring() -> tuple[list[dict], dict]:
    hybrid_rows = _read_csv(
        REPO_ROOT
        / "singpass-post-compromise-monitoring"
        / "hybrid_score"
        / "generated"
        / "post_login_hybrid_scores.csv"
    )
    feature_rows = _read_csv(
        REPO_ROOT
        / "singpass-post-compromise-monitoring"
        / "feature_engineering"
        / "generated"
        / "post_login_session_features.csv"
    )

    total_rows = len(hybrid_rows)
    fraud_rows = sum(1 for row in hybrid_rows if row["target_post_login_fraud_flag"] == "1")
    review_rows = sum(1 for row in hybrid_rows if row["hybrid_review_flag"] == "1")
    review_fraud_rows = sum(
        1 for row in hybrid_rows if row["hybrid_review_flag"] == "1" and row["target_post_login_fraud_flag"] == "1"
    )

    action_counter = Counter(row["hybrid_action"] for row in hybrid_rows)
    action_fraud_counter = Counter(
        row["hybrid_action"] for row in hybrid_rows if row["target_post_login_fraud_flag"] == "1"
    )
    band_counter = Counter(_score_band(float(row["ml_score"]), (0.3, 0.8)) for row in hybrid_rows)

    summary_rows = []
    for action in sorted(action_counter):
        total = action_counter[action]
        fraud = action_fraud_counter[action]
        summary_rows.append(
            {
                "scoring_name": "session_score",
                "metric_group": "action_distribution",
                "metric_key": action,
                "metric_value": total,
                "metric_rate": _pct(total, total_rows),
                "fraud_rows": fraud,
                "fraud_rate_within_group": _pct(fraud, total),
            }
        )

    for band in ["low", "medium", "high"]:
        total = band_counter[band]
        summary_rows.append(
            {
                "scoring_name": "session_score",
                "metric_group": "ml_score_band",
                "metric_key": band,
                "metric_value": total,
                "metric_rate": _pct(total, total_rows),
                "fraud_rows": "",
                "fraud_rate_within_group": "",
            }
        )

    first_sensitive_missing, first_sensitive_missing_rate = _null_rate(
        feature_rows, "time_to_first_sensitive_event_seconds"
    )
    first_switch_missing, first_switch_missing_rate = _null_rate(
        feature_rows, "time_to_first_service_switch_seconds"
    )

    summary = {
        "total_rows": total_rows,
        "fraud_rows": fraud_rows,
        "review_rows": review_rows,
        "review_rate": _pct(review_rows, total_rows),
        "recall": _pct(review_fraud_rows, fraud_rows),
        "precision": _pct(review_fraud_rows, review_rows),
        "time_to_first_sensitive_missing_rows": first_sensitive_missing,
        "time_to_first_sensitive_missing_rate": first_sensitive_missing_rate,
        "time_to_first_service_switch_missing_rows": first_switch_missing,
        "time_to_first_service_switch_missing_rate": first_switch_missing_rate,
    }
    return summary_rows, summary


def build_report(login_summary: dict, session_summary: dict) -> str:
    lines = [
        "# Portfolio Monitoring Report",
        "",
        f"Last updated: {datetime.now(timezone.utc).astimezone().strftime('%d %B %Y')}",
        "",
        "## Purpose",
        "",
        "This report converts the latest scored outputs into dashboard-ready operational summaries.",
        "",
        "## Login Score Monitoring",
        "",
        f"- total scored logins: {login_summary['total_rows']:,}",
        f"- fraud-labelled logins: {login_summary['fraud_rows']:,}",
        f"- reviewed logins: {login_summary['review_rows']:,}",
        f"- review rate: {login_summary['review_rate']}",
        f"- recall: {login_summary['recall']}",
        f"- precision: {login_summary['precision']}",
        f"- approval latency missing rate: {login_summary['approval_latency_missing_rate']}",
        f"- days-since-last-success missing rate: {login_summary['days_since_last_success_missing_rate']}",
        "",
        "## Session Score Monitoring",
        "",
        f"- total scored sessions: {session_summary['total_rows']:,}",
        f"- fraud-labelled sessions: {session_summary['fraud_rows']:,}",
        f"- reviewed sessions: {session_summary['review_rows']:,}",
        f"- review rate: {session_summary['review_rate']}",
        f"- recall: {session_summary['recall']}",
        f"- precision: {session_summary['precision']}",
        f"- first-sensitive-event missing rate: {session_summary['time_to_first_sensitive_missing_rate']}",
        f"- first-service-switch missing rate: {session_summary['time_to_first_service_switch_missing_rate']}",
        "",
        "## Notes",
        "",
        "- This is a static operational snapshot from the latest generated and scored outputs.",
        "- The selected operating points remain the project-level hybrid policies.",
        "- A later dashboard layer can consume the generated CSV summaries directly.",
    ]
    return "\n".join(lines) + "\n"


def main() -> None:
    login_rows, login_summary = build_login_monitoring()
    session_rows, session_summary = build_session_monitoring()

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    _write_csv(login_rows, OUTPUT_DIR / "login_score_monitoring.csv")
    _write_csv(session_rows, OUTPUT_DIR / "session_score_monitoring.csv")
    _write_text(build_report(login_summary, session_summary), OUTPUT_DIR / "portfolio_monitoring_report.md")
    _write_json(
        {
            "login_score": login_summary,
            "session_score": session_summary,
        },
        OUTPUT_DIR / "portfolio_monitoring_summary.json",
    )
    _write_json(
        {
            "generated_at_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
            "outputs": [
                "login_score_monitoring.csv",
                "session_score_monitoring.csv",
                "portfolio_monitoring_report.md",
                "portfolio_monitoring_summary.json",
            ],
        },
        OUTPUT_DIR / "last_monitoring_manifest.json",
    )
    print(f"Generated monitoring outputs in {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
