from __future__ import annotations

import csv
from collections import Counter, defaultdict
from pathlib import Path


RULE_WEIGHTS = {
    "R01_consent_granted_in_session": 3,
    "R02_signing_completed_in_session": 3,
    "R03_stacked_sensitive_activity": 3,
    "R04_sensitive_session_with_service_switching": 2,
    "R05_sensitive_session_without_benign_usage": 2,
    "R06_high_burst_sensitive_session": 2,
    "R07_first_time_sensitive_flow": 1,
}


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


def _to_int(value: str) -> int:
    if value in {"", None}:
        return 0
    return int(float(value))


def _risk_band(score: int) -> str:
    if score >= 5:
        return "critical"
    if score >= 3:
        return "high"
    if score >= 1:
        return "medium"
    return "low"


def _recommended_action(score: int) -> str:
    if score >= 5:
        return "restrict_or_manual_review"
    if score >= 3:
        return "manual_review"
    if score >= 1:
        return "allow_with_monitoring"
    return "allow"


def _evaluate_rules(row: dict) -> list[str]:
    triggered: list[str] = []

    if _to_int(row["has_any_consent_granted_flag"]) == 1:
        triggered.append("R01_consent_granted_in_session")

    if _to_int(row["has_any_sign_completed_flag"]) == 1:
        triggered.append("R02_signing_completed_in_session")

    if _to_int(row["sensitive_event_after_sensitive_event_flag"]) == 1:
        triggered.append("R03_stacked_sensitive_activity")

    if (
        _to_int(row["sensitive_event_count"]) >= 1
        and _to_int(row["service_switch_count"]) >= 1
        and _to_int(row["benign_service_usage_count"]) == 0
    ):
        triggered.append("R04_sensitive_session_with_service_switching")

    if _to_int(row["sensitive_event_count"]) >= 1 and _to_int(row["benign_service_usage_count"]) == 0:
        triggered.append("R05_sensitive_session_without_benign_usage")

    if _to_int(row["sensitive_event_count"]) >= 1 and _to_int(row["post_login_duration_seconds"]) <= 60:
        triggered.append("R06_high_burst_sensitive_session")

    if (
        _to_int(row["first_time_consent_flow_for_user_flag"]) == 1
        or _to_int(row["first_time_sign_flow_for_user_flag"]) == 1
    ):
        triggered.append("R07_first_time_sensitive_flow")

    return triggered


def build_rule_scores() -> tuple[list[dict], dict]:
    repo_root = Path(__file__).resolve().parents[3]
    feature_path = (
        repo_root
        / "singpass-post-compromise-monitoring"
        / "feature_engineering"
        / "generated"
        / "post_login_session_features.csv"
    )
    rows = _read_csv(feature_path)

    scored_rows: list[dict] = []
    rule_hits: Counter[str] = Counter()
    rule_fraud_hits: Counter[str] = Counter()
    risk_band_counts: dict[str, list[int]] = defaultdict(lambda: [0, 0])

    fraud_rows = 0
    flagged_rows = 0
    flagged_fraud_rows = 0
    review_rows = 0
    review_fraud_rows = 0

    for row in rows:
        target_flag = _to_int(row["target_post_login_fraud_flag"])
        fraud_rows += target_flag

        triggered_rules = _evaluate_rules(row)
        triggered_rule_count = len(triggered_rules)
        rule_score = sum(RULE_WEIGHTS[name] for name in triggered_rules)
        rule_band = _risk_band(rule_score)
        rule_flagged = 1 if triggered_rule_count > 0 else 0
        rule_review = 1 if rule_score >= 3 else 0
        action = _recommended_action(rule_score)

        if rule_flagged:
            flagged_rows += 1
            flagged_fraud_rows += target_flag
        if rule_review:
            review_rows += 1
            review_fraud_rows += target_flag

        for name in triggered_rules:
            rule_hits[name] += 1
            rule_fraud_hits[name] += target_flag

        risk_band_counts[rule_band][0] += 1
        risk_band_counts[rule_band][1] += target_flag

        scored_rows.append(
            {
                **row,
                "triggered_rule_count": triggered_rule_count,
                "triggered_rules": "|".join(triggered_rules),
                "rule_score": rule_score,
                "rule_risk_band": rule_band,
                "rule_flagged_session_flag": rule_flagged,
                "rule_review_flag": rule_review,
                "rule_recommended_action": action,
            }
        )

    metrics = {
        "rows": len(rows),
        "fraud_rows": fraud_rows,
        "flagged_rows": flagged_rows,
        "flagged_fraud_rows": flagged_fraud_rows,
        "review_rows": review_rows,
        "review_fraud_rows": review_fraud_rows,
        "rule_hits": rule_hits,
        "rule_fraud_hits": rule_fraud_hits,
        "risk_band_counts": risk_band_counts,
    }
    return scored_rows, metrics


def build_quality_report(metrics: dict) -> str:
    rows = metrics["rows"]
    fraud_rows = metrics["fraud_rows"]
    flagged_rows = metrics["flagged_rows"]
    flagged_fraud_rows = metrics["flagged_fraud_rows"]
    review_rows = metrics["review_rows"]
    review_fraud_rows = metrics["review_fraud_rows"]

    flag_rate = (flagged_rows / rows) if rows else 0.0
    flag_recall = (flagged_fraud_rows / fraud_rows) if fraud_rows else 0.0
    flag_precision = (flagged_fraud_rows / flagged_rows) if flagged_rows else 0.0
    review_rate = (review_rows / rows) if rows else 0.0
    review_recall = (review_fraud_rows / fraud_rows) if fraud_rows else 0.0
    review_precision = (review_fraud_rows / review_rows) if review_rows else 0.0

    lines = [
        "# Rule Quality Report",
        "",
        "Last updated: 12 April 2026",
        "",
        "## Dataset summary",
        "",
        f"- scored rows: {rows:,}",
        f"- fraud rows: {fraud_rows:,}",
        f"- flagged rows: {flagged_rows:,}",
        f"- flagged fraud rows: {flagged_fraud_rows:,}",
        f"- rule-layer flag rate: {flag_rate:.2%}",
        f"- rule-layer recall on fraud rows: {flag_recall:.2%}",
        f"- rule-layer precision on flagged rows: {flag_precision:.2%}",
        f"- review-threshold rows (score >= 3): {review_rows:,}",
        f"- review-threshold fraud rows: {review_fraud_rows:,}",
        f"- review-threshold rate: {review_rate:.2%}",
        f"- review-threshold recall on fraud rows: {review_recall:.2%}",
        f"- review-threshold precision: {review_precision:.2%}",
        "",
        "## Rule hit summary",
        "",
    ]

    for name, hits in sorted(metrics["rule_hits"].items()):
        fraud_hits = metrics["rule_fraud_hits"][name]
        precision = (fraud_hits / hits) if hits else 0.0
        lines.append(f"- `{name}`: hits={hits:,}, fraud_hits={fraud_hits:,}, precision={precision:.2%}")

    lines.extend(["", "## Risk-band summary", ""])
    for band in ["low", "medium", "high", "critical"]:
        rows_in_band, fraud_in_band = metrics["risk_band_counts"].get(band, [0, 0])
        fraud_rate = (fraud_in_band / rows_in_band) if rows_in_band else 0.0
        lines.append(f"- `{band}`: rows={rows_in_band:,}, fraud_rows={fraud_in_band:,}, fraud_rate={fraud_rate:.2%}")

    lines.extend(
        [
            "",
            "## Assessment",
            "",
            "- The rule layer is expected to be strong in project 2 because explicit downstream misuse is part of the post-login monitoring problem.",
            "- The review threshold should still be evaluated operationally rather than assumed to be final.",
            "- If the rule layer is already too close to deterministic, the ML layer should avoid over-relying on the same direct session summaries.",
        ]
    )

    return "\n".join(lines) + "\n"


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    output_dir = repo_root / "singpass-post-compromise-monitoring" / "rule_based_score" / "generated"
    rows, metrics = build_rule_scores()
    _write_csv(rows, output_dir / "post_login_rule_scores.csv")
    _write_text(build_quality_report(metrics), output_dir / "rule_quality_report.md")


if __name__ == "__main__":
    main()
