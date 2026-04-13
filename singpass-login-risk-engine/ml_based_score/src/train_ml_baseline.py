from __future__ import annotations

import json
from pathlib import Path

import joblib
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.metrics import accuracy_score, precision_score, recall_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder
from xgboost import XGBClassifier


NUMERIC_COLUMNS = [
    "approval_latency_seconds",
    "approval_latency_missing_flag",
    "login_hour_of_day",
    "service_supports_myinfo_flag",
    "service_supports_signing_flag",
    "user_device_link_exists_flag",
    "is_primary_device_flag",
    "new_country_for_user_flag",
    "new_region_for_user_flag",
    "new_asn_for_user_flag",
    "session_event_count_before_login",
    "session_failed_login_events_before_login",
    "session_rejected_login_events_before_login",
    "session_qr_request_count_before_login",
    "session_qr_prompt_count_before_login",
    "session_has_lifecycle_event_before_login_flag",
    "session_lifecycle_event_count_before_login",
    "session_has_contact_detail_updated_before_login_flag",
    "user_prior_login_count_7d",
    "user_prior_successful_login_count_7d",
    "user_prior_rejected_login_count_7d",
    "user_prior_distinct_services_30d",
    "user_prior_distinct_countries_30d",
    "user_prior_distinct_asns_30d",
    "days_since_last_successful_login",
    "days_since_last_successful_login_missing_flag",
    "device_prior_login_count_30d",
    "device_prior_distinct_users_30d",
    "device_used_by_multiple_users_flag",
    "first_time_service_for_user_flag",
    "service_used_by_user_last_30d_flag",
    "service_usage_count_by_user_30d",
]

CATEGORICAL_COLUMNS = [
    "login_event_type",
    "login_method",
    "channel",
    "service_sector_type",
    "service_risk_tier",
    "trust_status",
    "country",
    "region",
]


def _metrics(y_true: pd.Series, scores: pd.Series, threshold: float) -> dict[str, float]:
    preds = (scores >= threshold).astype(int)
    return {
        "threshold": threshold,
        "precision": precision_score(y_true, preds, zero_division=0),
        "recall": recall_score(y_true, preds, zero_division=0),
        "accuracy": accuracy_score(y_true, preds),
        "tp": int(((y_true == 1) & (preds == 1)).sum()),
        "fp": int(((y_true == 0) & (preds == 1)).sum()),
        "fn": int(((y_true == 1) & (preds == 0)).sum()),
        "tn": int(((y_true == 0) & (preds == 0)).sum()),
    }


def _build_pipeline(scale_pos_weight: float) -> Pipeline:
    numeric_transformer = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="constant", fill_value=0)),
        ]
    )
    categorical_transformer = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="constant", fill_value="unknown")),
            ("onehot", OneHotEncoder(handle_unknown="ignore")),
        ]
    )

    preprocessor = ColumnTransformer(
        transformers=[
            ("num", numeric_transformer, NUMERIC_COLUMNS),
            ("cat", categorical_transformer, CATEGORICAL_COLUMNS),
        ]
    )

    model = XGBClassifier(
        n_estimators=250,
        max_depth=4,
        learning_rate=0.05,
        subsample=0.9,
        colsample_bytree=0.9,
        objective="binary:logistic",
        eval_metric="logloss",
        scale_pos_weight=scale_pos_weight,
        random_state=42,
        n_jobs=4,
    )

    return Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            ("model", model),
        ]
    )


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    feature_path = repo_root / "singpass-login-risk-engine" / "feature_engineering" / "generated" / "login_features.csv"
    output_dir = repo_root / "singpass-login-risk-engine" / "ml_based_score" / "generated"
    output_dir.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(feature_path)
    df = df.sort_values(["event_timestamp", "event_id"]).reset_index(drop=True)
    target = df["target_login_fraud_flag"].astype(int)

    split_idx = int(len(df) * 0.8)
    feature_df = df[NUMERIC_COLUMNS + CATEGORICAL_COLUMNS].copy()
    x_train = feature_df.iloc[:split_idx]
    x_eval = feature_df.iloc[split_idx:]
    y_train = target.iloc[:split_idx]
    y_eval = target.iloc[split_idx:]

    fraud_rate = float(y_train.mean())
    scale_pos_weight = (1.0 - fraud_rate) / fraud_rate if fraud_rate > 0 else 1.0

    pipeline = _build_pipeline(scale_pos_weight=scale_pos_weight)
    pipeline.fit(x_train, y_train)

    train_scores = pd.Series(pipeline.predict_proba(x_train)[:, 1], index=x_train.index)
    eval_scores = pd.Series(pipeline.predict_proba(x_eval)[:, 1], index=x_eval.index)

    thresholds = [0.3, 0.5, 0.7]
    train_metric_rows = [_metrics(y_train, train_scores, threshold) for threshold in thresholds]
    eval_metric_rows = [_metrics(y_eval, eval_scores, threshold) for threshold in thresholds]

    score_df = pd.DataFrame(
        {
            "event_id": df["event_id"],
            "target_login_fraud_flag": target,
            "fraud_scenario": df["fraud_scenario"],
            "split_name": ["train"] * split_idx + ["eval"] * (len(df) - split_idx),
            "ml_score": pd.concat([train_scores, eval_scores]).sort_index(),
        }
    )
    score_df["ml_predicted_flag"] = (score_df["ml_score"] >= 0.5).astype(int)
    score_df.to_csv(output_dir / "login_ml_scores.csv", index=False)

    importance_df = pd.DataFrame(
        {
            "feature_name": pipeline.named_steps["preprocessor"].get_feature_names_out(),
            "importance_gain": pipeline.named_steps["model"].feature_importances_,
        }
    ).sort_values("importance_gain", ascending=False)
    importance_df.to_csv(output_dir / "feature_importance.csv", index=False)
    pipeline.named_steps["model"].save_model(output_dir / "xgb_model.json")
    joblib.dump(pipeline, output_dir / "serving_pipeline.joblib")

    serving_metadata = {
        "scoring_name": "login_score",
        "model_type": "xgboost_pipeline",
        "pipeline_artifact": "serving_pipeline.joblib",
        "numeric_features": NUMERIC_COLUMNS,
        "categorical_features": CATEGORICAL_COLUMNS,
        "default_ml_threshold": 0.5,
        "hybrid_policy_version": "v3",
    }
    (output_dir / "serving_metadata.json").write_text(json.dumps(serving_metadata, indent=2))

    report = [
        "# ML Evaluation Report",
        "",
        "Last updated: 11 April 2026",
        "",
        "## Model setup",
        "",
        "- baseline model: XGBoost classifier",
        "- runtime environment: Python 3.11 project virtual environment",
        "- split strategy: earliest 80% train, latest 20% evaluation by event timestamp",
        "- categorical handling: sklearn preprocessing pipeline with one-hot encoding",
        "- class weighting: `scale_pos_weight` derived from train fraud rate",
        "",
        "## Split summary",
        "",
        f"- train rows: {len(x_train):,}",
        f"- evaluation rows: {len(x_eval):,}",
        f"- train fraud rate: {y_train.mean():.2%}",
        f"- evaluation fraud rate: {y_eval.mean():.2%}",
        "",
        "## Train metrics by threshold",
        "",
    ]
    for metric in train_metric_rows:
        report.extend(
            [
                f"- threshold {metric['threshold']:.1f}: precision={metric['precision']:.2%}, recall={metric['recall']:.2%}, accuracy={metric['accuracy']:.2%}, tp/fp/fn/tn={metric['tp']}/{metric['fp']}/{metric['fn']}/{metric['tn']}",
            ]
        )

    report.extend(["", "## Evaluation metrics by threshold", ""])
    for metric in eval_metric_rows:
        report.extend(
            [
                f"- threshold {metric['threshold']:.1f}: precision={metric['precision']:.2%}, recall={metric['recall']:.2%}, accuracy={metric['accuracy']:.2%}, tp/fp/fn/tn={metric['tp']}/{metric['fp']}/{metric['fn']}/{metric['tn']}",
            ]
        )

    report.extend(["", "## Top feature importance", ""])
    for row in importance_df.head(10).itertuples(index=False):
        report.append(f"- `{row.feature_name}`: {row.importance_gain:.6f}")

    report.extend(
        [
            "",
            "## Outputs",
            "",
            "- `login_ml_scores.csv`",
            "- `feature_importance.csv`",
            "- `xgb_model.json`",
            "- `serving_pipeline.joblib`",
            "- `serving_metadata.json`",
            "",
            "## Notes",
            "",
            "- XGBoost is a better fit than the earlier hand-rolled linear baseline for this tabular fraud problem.",
            "- Project 1 now uses the same preprocessing-pipeline pattern as project 2 so training and API inference stay consistent.",
            "- The next comparison step should align ML thresholds against the tuned rule review threshold rather than relying only on `0.5`.",
        ]
    )

    (output_dir / "ml_evaluation_report.md").write_text("\n".join(report) + "\n")
    print(f"Generated ML baseline outputs in {output_dir}")


if __name__ == "__main__":
    main()
