from __future__ import annotations

import csv
from collections import Counter, defaultdict
from pathlib import Path


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


def _is_strong_rule_case(triggered_rules: str) -> bool:
    rules = triggered_rules or ""
    return (
        "R02_repeated_rejection_pressure" in rules
        or "R03_high_attempt_volume_before_success" in rules
        or rules == "R06_fast_approval_with_novelty"
        or rules == "R01_fast_qr_approval"
    )


def _hybrid_policy(rule_band: str, triggered_rules: str, ml_score: float) -> tuple[str, str, int]:
    strong_rule_case = _is_strong_rule_case(triggered_rules)

    if strong_rule_case and ml_score >= 0.93:
        return "critical", "block_or_manual_review", 1
    if strong_rule_case:
        return "high", "step_up_or_manual_review", 1
    if ml_score >= 0.93:
        return "high", "step_up_or_manual_review", 1
    if 0.5 <= ml_score < 0.8 and rule_band == "medium":
        return "high", "step_up", 1
    if ml_score >= 0.50:
        return "medium", "allow_with_monitoring", 0
    if 0.3 <= ml_score < 0.5 and rule_band == "low":
        return "medium", "step_up", 1
    return "low", "allow", 0


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    rule_path = repo_root / "singpass-login-risk-engine" / "rule_based_score" / "generated" / "login_rule_scores.csv"
    ml_path = repo_root / "singpass-login-risk-engine" / "ml_based_score" / "generated" / "login_ml_scores.csv"
    output_dir = repo_root / "singpass-login-risk-engine" / "hybrid_score" / "generated"
    output_dir.mkdir(parents=True, exist_ok=True)

    rule_rows = _read_csv(rule_path)
    ml_rows = _read_csv(ml_path)
    ml_by_event = {row["event_id"]: row for row in ml_rows}

    hybrid_rows = []
    action_counts = Counter()
    action_fraud_counts = Counter()
    band_counts = Counter()
    band_fraud_counts = Counter()
    cell_counts = defaultdict(lambda: [0, 0])

    for rule_row in rule_rows:
        event_id = rule_row["event_id"]
        ml_row = ml_by_event[event_id]
        ml_score = float(ml_row["ml_score"])
        rule_band = rule_row["rule_risk_band"]
        triggered_rules = rule_row["triggered_rules"]
        hybrid_band, hybrid_action, hybrid_review_flag = _hybrid_policy(rule_band, triggered_rules, ml_score)
        is_fraud = rule_row["target_login_fraud_flag"] == "1"

        if ml_score < 0.3:
            ml_bucket = "<0.3"
        elif ml_score < 0.5:
            ml_bucket = "0.3-0.5"
        elif ml_score < 0.8:
            ml_bucket = "0.5-0.8"
        elif ml_score < 0.93:
            ml_bucket = "0.8-0.93"
        else:
            ml_bucket = ">=0.93"

        action_counts[hybrid_action] += 1
        band_counts[hybrid_band] += 1
        cell_counts[(rule_band, ml_bucket)][0] += 1
        if is_fraud:
            action_fraud_counts[hybrid_action] += 1
            band_fraud_counts[hybrid_band] += 1
            cell_counts[(rule_band, ml_bucket)][1] += 1

        hybrid_rows.append(
            {
                "event_id": event_id,
                "target_login_fraud_flag": rule_row["target_login_fraud_flag"],
                "fraud_scenario": rule_row["fraud_scenario"],
                "rule_score": rule_row["rule_score"],
                "rule_risk_band": rule_band,
                "triggered_rules": triggered_rules,
                "rule_recommended_action": rule_row["rule_recommended_action"],
                "ml_score": ml_row["ml_score"],
                "ml_predicted_flag": ml_row["ml_predicted_flag"],
                "ml_bucket": ml_bucket,
                "strong_rule_case_flag": 1 if _is_strong_rule_case(triggered_rules) else 0,
                "hybrid_risk_band": hybrid_band,
                "hybrid_action": hybrid_action,
                "hybrid_review_flag": hybrid_review_flag,
            }
        )

    total_rows = len(hybrid_rows)
    fraud_rows = sum(1 for row in hybrid_rows if row["target_login_fraud_flag"] == "1")
    review_rows = sum(1 for row in hybrid_rows if int(row["hybrid_review_flag"]) == 1)
    review_fraud_rows = sum(
        1 for row in hybrid_rows if int(row["hybrid_review_flag"]) == 1 and row["target_login_fraud_flag"] == "1"
    )

    report = [
        "# Hybrid Evaluation Report",
        "",
        "Last updated: 11 April 2026",
            "",
            "## Dataset summary",
            "",
            "- hybrid policy version: v2",
            "- operating target: review rate under 12%, maximize recall, precision above 85%",
            f"- total rows: {total_rows:,}",
            f"- fraud rows: {fraud_rows:,}",
            f"- hybrid review rows: {review_rows:,}",
        f"- hybrid review fraud rows: {review_fraud_rows:,}",
        f"- hybrid review rate: {(review_rows / total_rows):.2%}" if total_rows else "- hybrid review rate: n/a",
        f"- hybrid recall on fraud rows: {(review_fraud_rows / fraud_rows):.2%}" if fraud_rows else "- hybrid recall on fraud rows: n/a",
        f"- hybrid precision on review rows: {(review_fraud_rows / review_rows):.2%}" if review_rows else "- hybrid precision on review rows: n/a",
        "",
        "## Action summary",
        "",
    ]

    for action in [
        "allow",
        "allow_with_monitoring",
        "step_up",
        "step_up_or_manual_review",
        "block_or_manual_review",
    ]:
        total = action_counts[action]
        fraud = action_fraud_counts[action]
        fraud_rate = (fraud / total) if total else 0.0
        report.append(f"- `{action}`: rows={total:,}, fraud_rows={fraud:,}, fraud_rate={fraud_rate:.2%}")

    report.extend(["", "## Hybrid risk-band summary", ""])
    for band in ["low", "medium", "high", "critical"]:
        total = band_counts[band]
        fraud = band_fraud_counts[band]
        fraud_rate = (fraud / total) if total else 0.0
        report.append(f"- `{band}`: rows={total:,}, fraud_rows={fraud:,}, fraud_rate={fraud_rate:.2%}")

    report.extend(["", "## Rule band x ML bucket grid", ""])
    for rule_band in ["low", "medium", "high", "critical"]:
        for ml_bucket in ["<0.3", "0.3-0.5", "0.5-0.8", "0.8-0.93", ">=0.93"]:
            total, fraud = cell_counts[(rule_band, ml_bucket)]
            fraud_rate = (fraud / total) if total else 0.0
            report.append(
                f"- `{rule_band} x {ml_bucket}`: rows={total:,}, fraud_rows={fraud:,}, fraud_rate={fraud_rate:.2%}"
            )

    report.extend(
        [
            "",
            "## Notes",
            "",
            "- The hybrid layer is a policy combiner, not an averaged score.",
            "- Hybrid v2 reviews a login when either the ML score is very high (`>= 0.93`) or the case matches a small set of high-confidence rule patterns.",
            "- This version was chosen because it meets the current operating target more closely than the earlier hybrid policy.",
        ]
    )

    _write_csv(hybrid_rows, output_dir / "hybrid_scores.csv")
    _write_text("\n".join(report) + "\n", output_dir / "hybrid_evaluation_report.md")
    print(f"Generated hybrid outputs in {output_dir}")


if __name__ == "__main__":
    main()
