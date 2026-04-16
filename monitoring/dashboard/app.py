from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import streamlit as st


REPO_ROOT = Path(__file__).resolve().parents[2]
MONITORING_DIR = REPO_ROOT / "monitoring" / "generated"

LOGIN_OPS_PATH = MONITORING_DIR / "login_score_ops.csv"
LOGIN_METRICS_PATH = MONITORING_DIR / "login_score_metrics.csv"
LOGIN_REVIEW_PATH = MONITORING_DIR / "login_score_review_cases.csv"
SESSION_OPS_PATH = MONITORING_DIR / "session_score_ops.csv"
SESSION_METRICS_PATH = MONITORING_DIR / "session_score_metrics.csv"
SESSION_REVIEW_PATH = MONITORING_DIR / "session_score_review_cases.csv"
REPORT_PATH = MONITORING_DIR / "portfolio_monitoring_report.md"
MANIFEST_PATH = MONITORING_DIR / "last_monitoring_manifest.json"
SUMMARY_PATH = MONITORING_DIR / "portfolio_monitoring_summary.json"


def _load_csv(path: Path) -> pd.DataFrame:
    return pd.read_csv(path)


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text())


def _safe_int(value) -> int:
    if pd.isna(value) or value == "":
        return 0
    return int(float(value))


def _action_df(df: pd.DataFrame) -> pd.DataFrame:
    filtered = df[df["metric_group"] == "action_distribution"].copy()
    filtered["metric_value"] = filtered["metric_value"].apply(_safe_int)
    filtered["fraud_rows"] = filtered["fraud_rows"].apply(_safe_int)
    return filtered.rename(
        columns={
            "metric_key": "action",
            "metric_value": "rows",
            "metric_rate": "row_rate",
            "fraud_rate_within_group": "fraud_rate_in_action",
        }
    )[["action", "rows", "row_rate", "fraud_rows", "fraud_rate_in_action"]]


def _scenario_df(df: pd.DataFrame) -> pd.DataFrame:
    filtered = df[df["metric_group"] == "reviewed_scenario_mix"].copy()
    filtered["metric_value"] = filtered["metric_value"].apply(_safe_int)
    filtered["fraud_rows"] = filtered["fraud_rows"].apply(_safe_int)
    return filtered.rename(
        columns={
            "metric_key": "scenario",
            "metric_value": "review_rows",
            "metric_rate": "review_share",
            "fraud_rate_within_group": "fraud_rate_in_reviewed_group",
        }
    )[["scenario", "review_rows", "review_share", "fraud_rows", "fraud_rate_in_reviewed_group"]]


def _score_band_df(df: pd.DataFrame) -> pd.DataFrame:
    filtered = df[df["metric_group"] == "ml_score_band"].copy()
    filtered["metric_value"] = filtered["metric_value"].apply(_safe_int)
    return filtered.rename(
        columns={
            "metric_key": "score_band",
            "metric_value": "rows",
            "metric_rate": "row_rate",
        }
    )[["score_band", "rows", "row_rate"]]


def _render_ops_view(
    title: str,
    ops_df: pd.DataFrame,
    review_df: pd.DataFrame,
    summary: dict,
    entity_label: str,
):
    st.subheader(title)
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Rows", f"{summary['total_rows']:,}")
    col2.metric("Review Rows", f"{summary['review_rows']:,}")
    col3.metric("Review Rate", summary["review_rate"])

    st.markdown("**Action Distribution**")
    action_df = _action_df(ops_df)
    st.bar_chart(action_df.set_index("action")["rows"])
    st.dataframe(action_df, use_container_width=True)

    st.markdown("**Reviewed Scenario Mix**")
    scenario_df = _scenario_df(ops_df)
    if not scenario_df.empty:
        st.bar_chart(scenario_df.set_index("scenario")["review_rows"])
        st.dataframe(scenario_df, use_container_width=True)
    else:
        st.info("No reviewed scenario mix is available.")

    st.markdown(f"**Top Reviewed {entity_label}**")
    st.dataframe(review_df, use_container_width=True)


def _render_metrics_view(
    title: str,
    metrics_df: pd.DataFrame,
    summary: dict,
    extra_metrics: list[tuple[str, str]],
):
    st.subheader(title)
    col1, col2, col3 = st.columns(3)
    col1.metric("Recall", summary["recall"])
    col2.metric("Precision", summary["precision"])
    col3.metric("Total Rows", f"{summary['total_rows']:,}")

    extra_cols = st.columns(len(extra_metrics))
    for col, (label, value) in zip(extra_cols, extra_metrics):
        col.metric(label, value)

    st.markdown("**ML Score Band Distribution**")
    band_df = _score_band_df(metrics_df)
    st.bar_chart(band_df.set_index("score_band")["rows"])
    st.dataframe(band_df, use_container_width=True)

    st.markdown("**Action Distribution from Metrics Surface**")
    action_df = _action_df(metrics_df)
    st.dataframe(action_df, use_container_width=True)


st.set_page_config(page_title="Singpass Anti-Fraud Monitoring", layout="wide")
st.title("Singpass Anti-Fraud Monitoring Dashboard")
st.caption("Operational dashboard built from the latest generated monitoring artifacts.")

required_paths = [
    LOGIN_OPS_PATH,
    LOGIN_METRICS_PATH,
    LOGIN_REVIEW_PATH,
    SESSION_OPS_PATH,
    SESSION_METRICS_PATH,
    SESSION_REVIEW_PATH,
    REPORT_PATH,
    MANIFEST_PATH,
    SUMMARY_PATH,
]
missing_paths = [path for path in required_paths if not path.exists()]
if missing_paths:
    st.error("Monitoring outputs are missing. Run the monitoring report generator first.")
    for path in missing_paths:
        st.code(str(path))
    st.stop()

login_ops_df = _load_csv(LOGIN_OPS_PATH)
login_metrics_df = _load_csv(LOGIN_METRICS_PATH)
login_review_df = _load_csv(LOGIN_REVIEW_PATH)
session_ops_df = _load_csv(SESSION_OPS_PATH)
session_metrics_df = _load_csv(SESSION_METRICS_PATH)
session_review_df = _load_csv(SESSION_REVIEW_PATH)
manifest = _load_json(MANIFEST_PATH)
summary = _load_json(SUMMARY_PATH)
report_text = REPORT_PATH.read_text()

overview1, overview2 = st.columns([2, 1])
with overview1:
    st.markdown("### Latest Run")
    st.write(f"Generated at UTC: `{manifest['generated_at_utc']}`")
    st.write("Artifacts:")
    for output in manifest.get("outputs", []):
        st.write(f"- `{output}`")
with overview2:
    st.markdown("### Portfolio Scope")
    st.write("- `login_score`: live login prevention")
    st.write("- `session_score`: post-login containment")

tabs = st.tabs(["Ops View", "Metrics View", "Report"])

with tabs[0]:
    st.markdown("## Ops View")
    st.caption("Operational workload, review queue composition, and drilldowns into reviewed items.")
    col1, col2 = st.columns(2)
    with col1:
        _render_ops_view(
            "Login Ops",
            login_ops_df,
            login_review_df,
            summary["login_score"]["ops"],
            entity_label="Login Cases",
        )
    with col2:
        _render_ops_view(
            "Session Ops",
            session_ops_df,
            session_review_df,
            summary["session_score"]["ops"],
            entity_label="Session Cases",
        )

with tabs[1]:
    st.markdown("## Metrics View")
    st.caption("Model performance, score distribution, and data-quality monitoring for parameter tuning.")
    col1, col2 = st.columns(2)
    with col1:
        _render_metrics_view(
            "Login Metrics",
            login_metrics_df,
            {
                **summary["login_score"]["ops"],
                **summary["login_score"]["metrics"],
            },
            extra_metrics=[
                ("Approval Latency Missing", summary["login_score"]["metrics"]["approval_latency_missing_rate"]),
                (
                    "Last Success Missing",
                    summary["login_score"]["metrics"]["days_since_last_success_missing_rate"],
                ),
            ],
        )
    with col2:
        _render_metrics_view(
            "Session Metrics",
            session_metrics_df,
            {
                **summary["session_score"]["ops"],
                **summary["session_score"]["metrics"],
            },
            extra_metrics=[
                (
                    "First Sensitive Missing",
                    summary["session_score"]["metrics"]["time_to_first_sensitive_missing_rate"],
                ),
                (
                    "First Switch Missing",
                    summary["session_score"]["metrics"]["time_to_first_service_switch_missing_rate"],
                ),
            ],
        )

with tabs[2]:
    st.markdown(report_text)
