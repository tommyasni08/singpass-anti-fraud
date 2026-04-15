from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import streamlit as st


REPO_ROOT = Path(__file__).resolve().parents[2]
MONITORING_DIR = REPO_ROOT / "monitoring" / "generated"
LOGIN_PATH = MONITORING_DIR / "login_score_monitoring.csv"
SESSION_PATH = MONITORING_DIR / "session_score_monitoring.csv"
REPORT_PATH = MONITORING_DIR / "portfolio_monitoring_report.md"
MANIFEST_PATH = MONITORING_DIR / "last_monitoring_manifest.json"
SUMMARY_PATH = MONITORING_DIR / "portfolio_monitoring_summary.json"


def _load_csv(path: Path) -> pd.DataFrame:
    return pd.read_csv(path)


def _load_manifest(path: Path) -> dict:
    return json.loads(path.read_text())


def _safe_int(value) -> int:
    if pd.isna(value) or value == "":
        return 0
    return int(float(value))


def _safe_str(value) -> str:
    if pd.isna(value):
        return ""
    return str(value)


def _metric_value(df: pd.DataFrame, metric_group: str, metric_key: str, column: str) -> str:
    filtered = df[(df["metric_group"] == metric_group) & (df["metric_key"] == metric_key)]
    if filtered.empty:
        return "n/a"
    return _safe_str(filtered.iloc[0][column])


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


def _render_score_panel(title: str, df: pd.DataFrame, total_rows: str, review_rate: str, recall: str, precision: str):
    st.subheader(title)
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Rows", total_rows)
    col2.metric("Review Rate", review_rate)
    col3.metric("Recall", recall)
    col4.metric("Precision", precision)

    st.markdown("**Action Distribution**")
    action_df = _action_df(df)
    st.bar_chart(action_df.set_index("action")["rows"])
    st.dataframe(action_df, use_container_width=True)

    st.markdown("**ML Score Band Distribution**")
    band_df = _score_band_df(df)
    st.bar_chart(band_df.set_index("score_band")["rows"])
    st.dataframe(band_df, use_container_width=True)


st.set_page_config(page_title="Singpass Anti-Fraud Monitoring", layout="wide")
st.title("Singpass Anti-Fraud Monitoring Dashboard")
st.caption("Operational dashboard built from the latest generated monitoring artifacts.")

missing_paths = [path for path in [LOGIN_PATH, SESSION_PATH, REPORT_PATH, MANIFEST_PATH, SUMMARY_PATH] if not path.exists()]
if missing_paths:
    st.error("Monitoring outputs are missing. Run the monitoring report generator first.")
    for path in missing_paths:
        st.code(str(path))
    st.stop()

login_df = _load_csv(LOGIN_PATH)
session_df = _load_csv(SESSION_PATH)
manifest = _load_manifest(MANIFEST_PATH)
summary = _load_manifest(SUMMARY_PATH)
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

tabs = st.tabs(["Overview", "Login Score", "Session Score", "Report"])

with tabs[0]:
    c1, c2 = st.columns(2)
    with c1:
        _render_score_panel(
            "Login Score Snapshot",
            login_df,
            total_rows=f"{summary['login_score']['total_rows']:,}",
            review_rate=summary["login_score"]["review_rate"],
            recall=summary["login_score"]["recall"],
            precision=summary["login_score"]["precision"],
        )
    with c2:
        _render_score_panel(
            "Session Score Snapshot",
            session_df,
            total_rows=f"{summary['session_score']['total_rows']:,}",
            review_rate=summary["session_score"]["review_rate"],
            recall=summary["session_score"]["recall"],
            precision=summary["session_score"]["precision"],
        )

with tabs[1]:
    _render_score_panel(
        "Login Score",
        login_df,
        total_rows=f"{summary['login_score']['total_rows']:,}",
        review_rate=summary["login_score"]["review_rate"],
        recall=summary["login_score"]["recall"],
        precision=summary["login_score"]["precision"],
    )

with tabs[2]:
    _render_score_panel(
        "Session Score",
        session_df,
        total_rows=f"{summary['session_score']['total_rows']:,}",
        review_rate=summary["session_score"]["review_rate"],
        recall=summary["session_score"]["recall"],
        precision=summary["session_score"]["precision"],
    )

with tabs[3]:
    st.markdown(report_text)
