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


def _scenario_mix_rows(
    rows: list[dict],
    scoring_name: str,
    scenario_key: str,
    target_key: str,
    review_key: str,
) -> list[dict]:
    reviewed = [row for row in rows if row[review_key] == "1"]
    total_reviewed = len(reviewed)
    scenario_counter = Counter(row[scenario_key] for row in reviewed)
    fraud_counter = Counter(row[scenario_key] for row in reviewed if row[target_key] == "1")
    out = []
    for scenario, total in sorted(scenario_counter.items(), key=lambda item: (-item[1], item[0])):
        fraud = fraud_counter[scenario]
        out.append(
            {
                "scoring_name": scoring_name,
                "metric_group": "reviewed_scenario_mix",
                "metric_key": scenario,
                "metric_value": total,
                "metric_rate": _pct(total, total_reviewed),
                "fraud_rows": fraud,
                "fraud_rate_within_group": _pct(fraud, total),
            }
        )
    return out


def _top_review_rows(
    rows: list[dict],
    scoring_name: str,
    entity_key: str,
    scenario_key: str,
    target_key: str,
    action_key: str,
    ml_score_key: str,
    limit: int = 25,
) -> list[dict]:
    reviewed = [row for row in rows if row["hybrid_review_flag"] == "1"]
    reviewed.sort(key=lambda row: (-float(row[ml_score_key]), row[entity_key]))
    out = []
    for row in reviewed[:limit]:
        out.append(
            {
                "scoring_name": scoring_name,
                "entity_id": row[entity_key],
                "fraud_scenario": row[scenario_key],
                "target_fraud_flag": row[target_key],
                "hybrid_action": row[action_key],
                "hybrid_risk_band": row["hybrid_risk_band"],
                "rule_score": row["rule_score"],
                "rule_risk_band": row["rule_risk_band"],
                "ml_score": row[ml_score_key],
            }
        )
    return out


def build_login_monitoring() -> tuple[list[dict], list[dict], list[dict], dict]:
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

    metrics_rows = []
    for action in sorted(action_counter):
        total = action_counter[action]
        fraud = action_fraud_counter[action]
        metrics_rows.append(
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
        metrics_rows.append(
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

    ops_rows = []
    for action in sorted(action_counter):
        total = action_counter[action]
        fraud = action_fraud_counter[action]
        ops_rows.append(
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
    ops_rows.extend(
        _scenario_mix_rows(
            hybrid_rows,
            scoring_name="login_score",
            scenario_key="fraud_scenario",
            target_key="target_login_fraud_flag",
            review_key="hybrid_review_flag",
        )
    )

    top_review = _top_review_rows(
        hybrid_rows,
        scoring_name="login_score",
        entity_key="event_id",
        scenario_key="fraud_scenario",
        target_key="target_login_fraud_flag",
        action_key="hybrid_action",
        ml_score_key="ml_score",
    )

    summary = {
        "ops": {
            "total_rows": total_rows,
            "fraud_rows": fraud_rows,
            "review_rows": review_rows,
            "review_rate": _pct(review_rows, total_rows),
        },
        "metrics": {
            "recall": _pct(review_fraud_rows, fraud_rows),
            "precision": _pct(review_fraud_rows, review_rows),
            "approval_latency_missing_rows": approval_missing,
            "approval_latency_missing_rate": approval_missing_rate,
            "days_since_last_success_missing_rows": last_success_missing,
            "days_since_last_success_missing_rate": last_success_missing_rate,
        },
    }
    return ops_rows, metrics_rows, top_review, summary


def build_session_monitoring() -> tuple[list[dict], list[dict], list[dict], dict]:
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

    metrics_rows = []
    for action in sorted(action_counter):
        total = action_counter[action]
        fraud = action_fraud_counter[action]
        metrics_rows.append(
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
        metrics_rows.append(
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

    ops_rows = []
    for action in sorted(action_counter):
        total = action_counter[action]
        fraud = action_fraud_counter[action]
        ops_rows.append(
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
    ops_rows.extend(
        _scenario_mix_rows(
            hybrid_rows,
            scoring_name="session_score",
            scenario_key="dominant_fraud_scenario",
            target_key="target_post_login_fraud_flag",
            review_key="hybrid_review_flag",
        )
    )

    top_review = _top_review_rows(
        hybrid_rows,
        scoring_name="session_score",
        entity_key="session_id",
        scenario_key="dominant_fraud_scenario",
        target_key="target_post_login_fraud_flag",
        action_key="hybrid_action",
        ml_score_key="ml_score",
    )

    summary = {
        "ops": {
            "total_rows": total_rows,
            "fraud_rows": fraud_rows,
            "review_rows": review_rows,
            "review_rate": _pct(review_rows, total_rows),
        },
        "metrics": {
            "recall": _pct(review_fraud_rows, fraud_rows),
            "precision": _pct(review_fraud_rows, review_rows),
            "time_to_first_sensitive_missing_rows": first_sensitive_missing,
            "time_to_first_sensitive_missing_rate": first_sensitive_missing_rate,
            "time_to_first_service_switch_missing_rows": first_switch_missing,
            "time_to_first_service_switch_missing_rate": first_switch_missing_rate,
        },
    }
    return ops_rows, metrics_rows, top_review, summary


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
        f"- total scored logins: {login_summary['ops']['total_rows']:,}",
        f"- fraud-labelled logins: {login_summary['ops']['fraud_rows']:,}",
        f"- reviewed logins: {login_summary['ops']['review_rows']:,}",
        f"- review rate: {login_summary['ops']['review_rate']}",
        f"- recall: {login_summary['metrics']['recall']}",
        f"- precision: {login_summary['metrics']['precision']}",
        f"- approval latency missing rate: {login_summary['metrics']['approval_latency_missing_rate']}",
        f"- days-since-last-success missing rate: {login_summary['metrics']['days_since_last_success_missing_rate']}",
        "",
        "## Session Score Monitoring",
        "",
        f"- total scored sessions: {session_summary['ops']['total_rows']:,}",
        f"- fraud-labelled sessions: {session_summary['ops']['fraud_rows']:,}",
        f"- reviewed sessions: {session_summary['ops']['review_rows']:,}",
        f"- review rate: {session_summary['ops']['review_rate']}",
        f"- recall: {session_summary['metrics']['recall']}",
        f"- precision: {session_summary['metrics']['precision']}",
        f"- first-sensitive-event missing rate: {session_summary['metrics']['time_to_first_sensitive_missing_rate']}",
        f"- first-service-switch missing rate: {session_summary['metrics']['time_to_first_service_switch_missing_rate']}",
        "",
        "## Notes",
        "",
        "- This is a static operational snapshot from the latest generated and scored outputs.",
        "- The selected operating points remain the project-level hybrid policies.",
        "- A later dashboard layer can consume the generated CSV summaries directly.",
    ]
    return "\n".join(lines) + "\n"


def main() -> None:
    login_ops_rows, login_metrics_rows, login_review_rows, login_summary = build_login_monitoring()
    session_ops_rows, session_metrics_rows, session_review_rows, session_summary = build_session_monitoring()

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    _write_csv(login_ops_rows, OUTPUT_DIR / "login_score_ops.csv")
    _write_csv(login_metrics_rows, OUTPUT_DIR / "login_score_metrics.csv")
    _write_csv(login_review_rows, OUTPUT_DIR / "login_score_review_cases.csv")
    _write_csv(session_ops_rows, OUTPUT_DIR / "session_score_ops.csv")
    _write_csv(session_metrics_rows, OUTPUT_DIR / "session_score_metrics.csv")
    _write_csv(session_review_rows, OUTPUT_DIR / "session_score_review_cases.csv")
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
                "login_score_ops.csv",
                "login_score_metrics.csv",
                "login_score_review_cases.csv",
                "session_score_ops.csv",
                "session_score_metrics.csv",
                "session_score_review_cases.csv",
                "portfolio_monitoring_report.md",
                "portfolio_monitoring_summary.json",
            ],
        },
        OUTPUT_DIR / "last_monitoring_manifest.json",
    )
    print(f"Generated monitoring outputs in {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
