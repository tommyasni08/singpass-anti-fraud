from __future__ import annotations

import argparse
import json
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path


@dataclass(frozen=True)
class Step:
    name: str
    script_path: str


REPO_ROOT = Path(__file__).resolve().parents[2]
PIPELINES_DIR = REPO_ROOT / "pipelines"
MANIFEST_PATH = PIPELINES_DIR / "generated" / "last_run_manifest.json"


PIPELINE_TARGETS: dict[str, list[Step]] = {
    "shared_data": [
        Step("shared_data_generation", "data/data_generator/src/generate_dataset.py"),
    ],
    "login_score": [
        Step("login_feature_engineering", "singpass-login-risk-engine/feature_engineering/src/generate_login_features.py"),
        Step("login_rule_scoring", "singpass-login-risk-engine/rule_based_score/src/generate_rule_scores.py"),
        Step("login_ml_training", "singpass-login-risk-engine/ml_based_score/src/train_ml_baseline.py"),
        Step("login_hybrid_scoring", "singpass-login-risk-engine/hybrid_score/src/generate_hybrid_scores.py"),
    ],
    "session_score": [
        Step(
            "session_feature_engineering",
            "singpass-post-compromise-monitoring/feature_engineering/src/generate_post_login_session_features.py",
        ),
        Step(
            "session_rule_scoring",
            "singpass-post-compromise-monitoring/rule_based_score/src/generate_rule_scores.py",
        ),
        Step(
            "session_ml_training",
            "singpass-post-compromise-monitoring/ml_based_score/src/train_ml_baseline.py",
        ),
        Step(
            "session_hybrid_scoring",
            "singpass-post-compromise-monitoring/hybrid_score/src/generate_hybrid_scores.py",
        ),
    ],
}

PIPELINE_TARGETS["full_rebuild"] = (
    PIPELINE_TARGETS["shared_data"] + PIPELINE_TARGETS["login_score"] + PIPELINE_TARGETS["session_score"]
)


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _list_targets() -> str:
    lines = ["Available pipeline targets:", ""]
    for target_name in ["shared_data", "login_score", "session_score", "full_rebuild"]:
        lines.append(f"- {target_name}")
    return "\n".join(lines)


def _run_step(step: Step) -> None:
    script_path = REPO_ROOT / step.script_path
    if not script_path.exists():
        raise FileNotFoundError(f"Pipeline step script not found: {script_path}")

    print(f"[pipeline] starting step: {step.name}")
    subprocess.run([sys.executable, str(script_path)], cwd=REPO_ROOT, check=True)
    print(f"[pipeline] completed step: {step.name}")


def _write_manifest(target: str, started_at: str, completed_at: str, step_names: list[str]) -> None:
    MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)
    manifest = {
        "target": target,
        "started_at_utc": started_at,
        "completed_at_utc": completed_at,
        "python_executable": Path(sys.executable).name,
        "virtual_environment_hint": "singpass_anti_fraud_venv",
        "steps": step_names,
    }
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser(description="Run orchestration jobs for the Singpass anti-fraud portfolio.")
    parser.add_argument("--target", choices=sorted(PIPELINE_TARGETS.keys()))
    parser.add_argument("--list", action="store_true", help="List available pipeline targets.")
    args = parser.parse_args()

    if args.list:
        print(_list_targets())
        return

    if not args.target:
        parser.error("either --target or --list is required")

    steps = PIPELINE_TARGETS[args.target]
    started_at = _utc_now()

    for step in steps:
        _run_step(step)

    completed_at = _utc_now()
    _write_manifest(args.target, started_at, completed_at, [step.name for step in steps])
    print(f"[pipeline] wrote manifest to {MANIFEST_PATH}")


if __name__ == "__main__":
    main()
