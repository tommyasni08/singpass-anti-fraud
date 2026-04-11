from __future__ import annotations

import csv
from collections import Counter, defaultdict
from pathlib import Path


RULE_WEIGHTS = {
    "R01_fast_qr_approval": 2,
    "R02_repeated_rejection_pressure": 3,
    "R03_high_attempt_volume_before_success": 3,
    "R04_foreign_and_new_country": 2,
    "R06_fast_approval_with_novelty": 3,
    "R07_prior_rejection_history_plus_success": 2,
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


def _to_float(value: str) -> float | None:
    if value in {"", None}:
        return None
    return float(value)


def _to_int(value: str) -> int:
    return int(value)


def _risk_band(score: int) -> str:
    if score >= 5:
        return "critical"
    if score >= 3:
        return "high"
    if score >= 1:
        return "medium"
    return "low"


def _recommended_action(risk_band: str) -> str:
    if risk_band == "critical":
        return "block_or_manual_review"
    if risk_band == "high":
        return "step_up_or_manual_review"
    if risk_band == "medium":
        return "allow_with_monitoring"
    return "allow"


def _apply_rules(row: dict) -> list[str]:
    rules: list[str] = []
    latency = _to_float(row["approval_latency_seconds"])
    novelty_count = sum(
        _to_int(row[col])
        for col in ["new_country_for_user_flag", "new_region_for_user_flag", "new_asn_for_user_flag"]
    )

    if row["login_event_type"] == "qr_login_approved" and latency is not None and latency <= 2.0:
        rules.append("R01_fast_qr_approval")

    if _to_int(row["session_rejected_login_events_before_login"]) >= 2:
        rules.append("R02_repeated_rejection_pressure")

    if _to_int(row["session_qr_request_count_before_login"]) >= 4:
        rules.append("R03_high_attempt_volume_before_success")

    if (
        row["country"] != "SG"
        and _to_int(row["new_country_for_user_flag"]) == 1
        and latency is not None
        and latency <= 2.0
    ):
        rules.append("R04_foreign_and_new_country")

    if latency is not None and latency <= 2.0 and novelty_count >= 1:
        rules.append("R06_fast_approval_with_novelty")

    if _to_int(row["user_prior_rejected_login_count_7d"]) >= 2:
        rules.append("R07_prior_rejection_history_plus_success")

    return rules


def build_rule_scores() -> tuple[list[dict], str]:
    repo_root = Path(__file__).resolve().parents[3]
    feature_dir = repo_root / "singpass-login-risk-engine" / "feature_engineering" / "generated"
    rows = _read_csv(feature_dir / "login_features.csv")

    scored_rows: list[dict] = []
    rule_totals = Counter()
    rule_fraud_hits = Counter()
    risk_band_totals = Counter()
    risk_band_fraud = Counter()

    for row in rows:
        triggered_rules = _apply_rules(row)
        rule_score = sum(RULE_WEIGHTS[rule] for rule in triggered_rules)
        risk_band = _risk_band(rule_score)
        is_fraud = row["target_login_fraud_flag"] == "1"

        for rule in triggered_rules:
            rule_totals[rule] += 1
            if is_fraud:
                rule_fraud_hits[rule] += 1

        risk_band_totals[risk_band] += 1
        if is_fraud:
            risk_band_fraud[risk_band] += 1

        scored_rows.append(
            {
                **row,
                "triggered_rule_count": len(triggered_rules),
                "triggered_rules": "|".join(triggered_rules),
                "rule_score": rule_score,
                "rule_risk_band": risk_band,
                "rule_flagged_login_flag": 1 if rule_score > 0 else 0,
                "rule_review_flag": 1 if rule_score >= 3 else 0,
                "rule_recommended_action": _recommended_action(risk_band),
            }
        )

    total_rows = len(scored_rows)
    fraud_rows = sum(1 for row in scored_rows if row["target_login_fraud_flag"] == "1")
    flagged_rows = sum(1 for row in scored_rows if int(row["rule_flagged_login_flag"]) == 1)
    flagged_fraud_rows = sum(
        1 for row in scored_rows if int(row["rule_flagged_login_flag"]) == 1 and row["target_login_fraud_flag"] == "1"
    )
    review_rows = sum(1 for row in scored_rows if int(row["rule_review_flag"]) == 1)
    review_fraud_rows = sum(
        1 for row in scored_rows if int(row["rule_review_flag"]) == 1 and row["target_login_fraud_flag"] == "1"
    )

    report = [
        "# Rule Quality Report",
        "",
        "Last updated: 11 April 2026",
        "",
        "## Dataset summary",
        "",
        f"- scored rows: {total_rows:,}",
        f"- fraud rows: {fraud_rows:,}",
        f"- flagged rows: {flagged_rows:,}",
        f"- flagged fraud rows: {flagged_fraud_rows:,}",
        f"- rule-layer flag rate: {(flagged_rows / total_rows):.2%}" if total_rows else "- rule-layer flag rate: n/a",
        f"- rule-layer recall on fraud rows: {(flagged_fraud_rows / fraud_rows):.2%}" if fraud_rows else "- rule-layer recall on fraud rows: n/a",
        f"- rule-layer precision on flagged rows: {(flagged_fraud_rows / flagged_rows):.2%}" if flagged_rows else "- rule-layer precision on flagged rows: n/a",
        f"- review-threshold rows (score >= 3): {review_rows:,}",
        f"- review-threshold fraud rows: {review_fraud_rows:,}",
        f"- review-threshold rate: {(review_rows / total_rows):.2%}" if total_rows else "- review-threshold rate: n/a",
        f"- review-threshold recall on fraud rows: {(review_fraud_rows / fraud_rows):.2%}" if fraud_rows else "- review-threshold recall on fraud rows: n/a",
        f"- review-threshold precision: {(review_fraud_rows / review_rows):.2%}" if review_rows else "- review-threshold precision: n/a",
        "",
        "## Rule hit summary",
        "",
    ]

    for rule_name in RULE_WEIGHTS:
        hits = rule_totals[rule_name]
        fraud_hits = rule_fraud_hits[rule_name]
        precision = (fraud_hits / hits) if hits else 0.0
        report.append(
            f"- `{rule_name}`: hits={hits:,}, fraud_hits={fraud_hits:,}, precision={precision:.2%}"
        )

    report.extend(["", "## Risk-band summary", ""])
    for band in ["low", "medium", "high", "critical"]:
        total = risk_band_totals[band]
        fraud = risk_band_fraud[band]
        fraud_rate = (fraud / total) if total else 0.0
        report.append(f"- `{band}`: rows={total:,}, fraud_rows={fraud:,}, fraud_rate={fraud_rate:.2%}")

    report.extend(
        [
            "",
            "## Assessment",
            "",
            "- The rule layer is intended to catch the clearest suspicious access patterns, not every fraud case.",
            "- High precision on specific rules is more important than broad coverage for the first baseline.",
            "- The ML layer should later absorb weaker, multi-feature patterns that do not warrant hard rules on their own.",
            "- For operations, `score >= 3` is the more realistic review threshold than `any hit`.",
        ]
    )

    return scored_rows, "\n".join(report) + "\n"


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    output_dir = repo_root / "singpass-login-risk-engine" / "rule_based_score" / "generated"
    scored_rows, report = build_rule_scores()
    _write_csv(scored_rows, output_dir / "login_rule_scores.csv")
    _write_text(report, output_dir / "rule_quality_report.md")
    print(f"Generated rule scores in {output_dir}")


if __name__ == "__main__":
    main()
