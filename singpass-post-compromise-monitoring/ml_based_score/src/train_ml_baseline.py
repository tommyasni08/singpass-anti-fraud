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


NUMERIC_FEATURES = [
    "post_login_duration_seconds",
    "distinct_service_count_in_session",
    "time_to_first_post_login_event_seconds",
    "time_to_first_service_switch_seconds",
    "time_to_first_service_switch_missing_flag",
    "max_event_burst_5m",
    "service_switch_count",
    "service_used_by_user_last_30d_flag",
    "service_usage_count_by_user_30d",
    "rare_service_access_flag",
    "high_risk_service_access_flag",
    "user_prior_monitored_session_count_30d",
    "user_prior_sensitive_session_count_30d",
    "user_prior_distinct_services_30d",
    "user_prior_avg_post_login_event_count_30d",
    "user_prior_avg_session_duration_seconds_30d",
    "session_event_count_deviation_from_user_avg",
    "session_event_count_deviation_missing_flag",
    "session_duration_deviation_from_user_avg",
    "session_duration_deviation_missing_flag",
    "login_hour_of_day",
    "recent_lifecycle_change_before_session_flag",
    "recent_contact_detail_update_before_session_flag",
    "recent_app_reinstall_before_session_flag",
]

CATEGORICAL_FEATURES = [
    "service_sector_type",
    "service_risk_tier",
    "login_method",
    "login_country",
    "trust_status",
]

TARGET_COLUMN = "target_post_login_fraud_flag"
TIMESTAMP_COLUMN = "login_timestamp"
ID_COLUMN = "session_id"


def _load_data() -> pd.DataFrame:
    repo_root = Path(__file__).resolve().parents[3]
    path = (
        repo_root
        / "singpass-post-compromise-monitoring"
        / "feature_engineering"
        / "generated"
        / "post_login_session_features.csv"
    )
    df = pd.read_csv(path)
    df[TIMESTAMP_COLUMN] = pd.to_datetime(df[TIMESTAMP_COLUMN])
    df[TARGET_COLUMN] = df[TARGET_COLUMN].astype(int)
    return df.sort_values(TIMESTAMP_COLUMN).reset_index(drop=True)


def _split_data(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    split_idx = int(len(df) * 0.8)
    train_df = df.iloc[:split_idx].copy()
    eval_df = df.iloc[split_idx:].copy()
    return train_df, eval_df


def _build_model(scale_pos_weight: float) -> Pipeline:
    numeric_transformer = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="constant", fill_value=0)),
        ]
    )
    categorical_transformer = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("onehot", OneHotEncoder(handle_unknown="ignore")),
        ]
    )

    preprocessor = ColumnTransformer(
        transformers=[
            ("num", numeric_transformer, NUMERIC_FEATURES),
            ("cat", categorical_transformer, CATEGORICAL_FEATURES),
        ]
    )

    model = XGBClassifier(
        n_estimators=250,
        max_depth=4,
        learning_rate=0.08,
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


def _evaluate_threshold(y_true: pd.Series, scores: pd.Series, threshold: float) -> dict:
    preds = (scores >= threshold).astype(int)
    return {
        "threshold": threshold,
        "precision": precision_score(y_true, preds, zero_division=0),
        "recall": recall_score(y_true, preds, zero_division=0),
        "accuracy": accuracy_score(y_true, preds),
        "tp": int(((preds == 1) & (y_true == 1)).sum()),
        "fp": int(((preds == 1) & (y_true == 0)).sum()),
        "fn": int(((preds == 0) & (y_true == 1)).sum()),
        "tn": int(((preds == 0) & (y_true == 0)).sum()),
    }


def _format_metric_line(prefix: str, metrics: dict) -> str:
    return (
        f"- threshold {metrics['threshold']:.1f}: precision={metrics['precision']:.2%}, "
        f"recall={metrics['recall']:.2%}, accuracy={metrics['accuracy']:.2%}, "
        f"tp/fp/fn/tn={metrics['tp']}/{metrics['fp']}/{metrics['fn']}/{metrics['tn']}"
    )


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    output_dir = repo_root / "singpass-post-compromise-monitoring" / "ml_based_score" / "generated"
    output_dir.mkdir(parents=True, exist_ok=True)

    df = _load_data()
    train_df, eval_df = _split_data(df)

    train_x = train_df[NUMERIC_FEATURES + CATEGORICAL_FEATURES]
    train_y = train_df[TARGET_COLUMN]
    eval_x = eval_df[NUMERIC_FEATURES + CATEGORICAL_FEATURES]
    eval_y = eval_df[TARGET_COLUMN]

    train_pos = int(train_y.sum())
    train_neg = int((train_y == 0).sum())
    scale_pos_weight = (train_neg / train_pos) if train_pos else 1.0

    pipeline = _build_model(scale_pos_weight=scale_pos_weight)
    pipeline.fit(train_x, train_y)

    train_scores = pd.Series(pipeline.predict_proba(train_x)[:, 1], index=train_df.index)
    eval_scores = pd.Series(pipeline.predict_proba(eval_x)[:, 1], index=eval_df.index)

    thresholds = [0.3, 0.5, 0.7]
    train_metrics = [_evaluate_threshold(train_y, train_scores, threshold) for threshold in thresholds]
    eval_metrics = [_evaluate_threshold(eval_y, eval_scores, threshold) for threshold in thresholds]

    combined = pd.concat(
        [
            train_df[[ID_COLUMN, TARGET_COLUMN]].assign(
                ml_score=train_scores.values,
                split_name="train",
                ml_predicted_flag=(train_scores >= 0.5).astype(int).values,
            ),
            eval_df[[ID_COLUMN, TARGET_COLUMN]].assign(
                ml_score=eval_scores.values,
                split_name="evaluation",
                ml_predicted_flag=(eval_scores >= 0.5).astype(int).values,
            ),
        ],
        ignore_index=True,
    )
    combined.to_csv(output_dir / "post_login_ml_scores.csv", index=False)

    preprocessor = pipeline.named_steps["preprocessor"]
    model = pipeline.named_steps["model"]
    feature_names = preprocessor.get_feature_names_out()
    importance_df = pd.DataFrame(
        {
            "feature_name": feature_names,
            "importance": model.feature_importances_,
        }
    ).sort_values("importance", ascending=False)
    importance_df.to_csv(output_dir / "feature_importance.csv", index=False)
    model.save_model(output_dir / "xgb_model.json")
    joblib.dump(pipeline, output_dir / "serving_pipeline.joblib")

    serving_metadata = {
        "scoring_name": "session_score",
        "model_type": "xgboost_pipeline",
        "pipeline_artifact": "serving_pipeline.joblib",
        "numeric_features": NUMERIC_FEATURES,
        "categorical_features": CATEGORICAL_FEATURES,
        "default_ml_threshold": 0.5,
        "hybrid_policy_version": "v1",
        "hybrid_ml_review_threshold": 0.3,
    }
    (output_dir / "serving_metadata.json").write_text(json.dumps(serving_metadata, indent=2))

    report_lines = [
        "# ML Evaluation Report",
        "",
        "Last updated: 12 April 2026",
        "",
        "## Model setup",
        "",
        "- baseline model: XGBoost classifier",
        "- runtime environment: Python 3.11 project virtual environment",
        "- split strategy: earliest 80% train, latest 20% evaluation by login timestamp",
        "- categorical handling: one-hot encoding",
        "- class weighting: `scale_pos_weight` derived from train fraud rate",
        "",
        "## Split summary",
        "",
        f"- train rows: {len(train_df):,}",
        f"- evaluation rows: {len(eval_df):,}",
        f"- train fraud rate: {train_y.mean():.2%}",
        f"- evaluation fraud rate: {eval_y.mean():.2%}",
        "",
        "## Train metrics by threshold",
        "",
    ]
    report_lines.extend(_format_metric_line("train", metric) for metric in train_metrics)
    report_lines.extend(["", "## Evaluation metrics by threshold", ""])
    report_lines.extend(_format_metric_line("evaluation", metric) for metric in eval_metrics)

    report_lines.extend(["", "## Top feature importance", ""])
    for _, row in importance_df.head(10).iterrows():
        report_lines.append(f"- `{row['feature_name']}`: {row['importance']:.6f}")

    report_lines.extend(
        [
            "",
            "## Notes",
            "",
            "- This baseline intentionally excludes the clearest direct post-login completion flags already covered by the rule layer.",
            "- The purpose of this model is to test whether broader session-shape and behavioural features add value beyond explicit containment rules.",
            "- `serving_pipeline.joblib` is exported for API inference so preprocessing and model scoring stay consistent.",
        ]
    )

    (output_dir / "ml_evaluation_report.md").write_text("\n".join(report_lines) + "\n")


if __name__ == "__main__":
    main()
