from __future__ import annotations

from functools import lru_cache
from pathlib import Path


@lru_cache(maxsize=1)
def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def login_ml_dir() -> Path:
    return repo_root() / "singpass-login-risk-engine" / "ml_based_score" / "generated"


def login_feature_path() -> Path:
    return repo_root() / "singpass-login-risk-engine" / "feature_engineering" / "generated" / "login_features.csv"


def session_ml_dir() -> Path:
    return repo_root() / "singpass-post-compromise-monitoring" / "ml_based_score" / "generated"


def session_feature_path() -> Path:
    return (
        repo_root()
        / "singpass-post-compromise-monitoring"
        / "feature_engineering"
        / "generated"
        / "post_login_session_features.csv"
    )
