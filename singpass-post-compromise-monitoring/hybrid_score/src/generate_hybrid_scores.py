from __future__ import annotations

import csv
from pathlib import Path


ML_REVIEW_THRESHOLD = 0.3


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


def build_hybrid_scores() -> tuple[list[dict], dict]:
    repo_root = Path(__file__).resolve().parents[3]
    rule_path = (
        repo_root
        / "singpass-post-compromise-monitoring"
        / "rule_based_score"
        / "generated"
        / "post_login_rule_scores.csv"
    )
    ml_path = (
        repo_root
        / "singpass-post-compromise-monitoring"
        / "ml_based_score"
        / "generated"
        / "post_login_ml_scores.csv"
    )

    rule_rows = _read_csv(rule_path)
    ml_map = {row["session_id"]: row for row in _read_csv(ml_path)}

    scored_rows: list[dict] = []
    total_rows = 0
    fraud_rows = 0
    review_rows = 0
    review_fraud_rows = 0
    action_counts: dict[str, list[int]] = {}

    for rule_row in rule_rows:
        session_id = rule_row["session_id"]
        ml_row = ml_map[session_id]
        target_flag = int(rule_row["target_post_login_fraud_flag"])
        ml_score = float(ml_row["ml_score"])
        rule_review_flag = int(rule_row["rule_review_flag"])
        rule_band = rule_row["rule_risk_band"]

        if rule_band == "critical":
            hybrid_action = "restrict_or_manual_review"
            hybrid_risk_band = "critical"
            hybrid_review_flag = 1
        elif rule_review_flag == 1:
            hybrid_action = "manual_review"
            hybrid_risk_band = "high"
            hybrid_review_flag = 1
        elif ml_score >= ML_REVIEW_THRESHOLD:
            hybrid_action = "review_due_to_behavioral_risk"
            hybrid_risk_band = "medium"
            hybrid_review_flag = 1
        else:
            hybrid_action = "allow"
            hybrid_risk_band = "low"
            hybrid_review_flag = 0

        total_rows += 1
        fraud_rows += target_flag
        review_rows += hybrid_review_flag
        review_fraud_rows += target_flag if hybrid_review_flag else 0
        action_counts.setdefault(hybrid_action, [0, 0])
        action_counts[hybrid_action][0] += 1
        action_counts[hybrid_action][1] += target_flag

        scored_rows.append(
            {
                "session_id": session_id,
                "target_post_login_fraud_flag": target_flag,
                "dominant_fraud_scenario": rule_row["dominant_fraud_scenario"],
                "rule_score": rule_row["rule_score"],
                "rule_risk_band": rule_band,
                "ml_score": ml_score,
                "ml_predicted_flag": 1 if ml_score >= 0.5 else 0,
                "hybrid_risk_band": hybrid_risk_band,
                "hybrid_action": hybrid_action,
                "hybrid_review_flag": hybrid_review_flag,
            }
        )

    metrics = {
        "total_rows": total_rows,
        "fraud_rows": fraud_rows,
        "review_rows": review_rows,
        "review_fraud_rows": review_fraud_rows,
        "action_counts": action_counts,
    }
    return scored_rows, metrics


def build_report(metrics: dict) -> str:
    total_rows = metrics["total_rows"]
    fraud_rows = metrics["fraud_rows"]
    review_rows = metrics["review_rows"]
    review_fraud_rows = metrics["review_fraud_rows"]
    review_rate = review_rows / total_rows if total_rows else 0.0
    recall = review_fraud_rows / fraud_rows if fraud_rows else 0.0
    precision = review_fraud_rows / review_rows if review_rows else 0.0

    lines = [
        "# Hybrid Evaluation Report",
        "",
        "Last updated: 12 April 2026",
        "",
        "## Dataset summary",
        "",
        "- hybrid policy version: v1",
        "- operating priority: maximize containment recall",
        f"- total rows: {total_rows:,}",
        f"- fraud rows: {fraud_rows:,}",
        f"- hybrid review rows: {review_rows:,}",
        f"- hybrid review fraud rows: {review_fraud_rows:,}",
        f"- hybrid review rate: {review_rate:.2%}",
        f"- hybrid recall on fraud rows: {recall:.2%}",
        f"- hybrid precision on review rows: {precision:.2%}",
        "",
        "## Action summary",
        "",
    ]

    for action in [
        "allow",
        "review_due_to_behavioral_risk",
        "manual_review",
        "restrict_or_manual_review",
    ]:
        rows, fraud = metrics["action_counts"].get(action, [0, 0])
        fraud_rate = fraud / rows if rows else 0.0
        lines.append(f"- `{action}`: rows={rows:,}, fraud_rows={fraud:,}, fraud_rate={fraud_rate:.2%}")

    lines.extend(
        [
            "",
            "## Notes",
            "",
            f"- The hybrid policy reviews any session that either matches the tuned rule layer or has `ml_score >= {ML_REVIEW_THRESHOLD}`.",
            "- This operating point was selected because project 2 prioritizes containment recall over minimizing review volume.",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    output_dir = repo_root / "singpass-post-compromise-monitoring" / "hybrid_score" / "generated"
    rows, metrics = build_hybrid_scores()
    _write_csv(rows, output_dir / "post_login_hybrid_scores.csv")
    _write_text(build_report(metrics), output_dir / "hybrid_evaluation_report.md")


if __name__ == "__main__":
    main()
