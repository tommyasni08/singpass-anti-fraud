# Pipelines

This folder contains orchestration jobs for the Singpass anti-fraud portfolio.

The pipelines layer does not replace the existing generator, feature, rule, ML, or hybrid modules. It wraps them into runnable jobs so the repository reads more like a production workflow:

- shared data generation
- login-score feature and model pipeline
- session-score feature and model pipeline
- full portfolio rebuild

## Purpose

The repository already has the core modeling logic in the project folders. The pipelines layer adds a thin operational boundary:

- one command to refresh shared synthetic data
- one command to rebuild the login scoring stack
- one command to rebuild the session monitoring stack
- one command to rebuild the full portfolio end to end

This is the correct foundation for later work such as:

- scheduled retraining
- model metrics monitoring
- dashboard input preparation
- batch scoring jobs

## Entrypoint

From the repository root:

```bash
python pipelines/src/run_pipeline.py --list
```

Run a named pipeline target:

```bash
python pipelines/src/run_pipeline.py --target login_score
```

If you prefer not to activate the environment first, use the project virtual environment explicitly:

```bash
./singpass_anti_fraud_venv/bin/python pipelines/src/run_pipeline.py --target login_score
```

## Supported targets

- `shared_data`
  - regenerate the shared synthetic backend tables
- `login_score`
  - rebuild project-1 feature, rule, ML, and hybrid outputs from the current shared data
- `session_score`
  - rebuild project-2 feature, rule, ML, and hybrid outputs from the current shared data
- `full_rebuild`
  - regenerate shared data, then rebuild both project pipelines

## Run manifest

Each successful pipeline run writes:

```text
pipelines/generated/last_run_manifest.json
```

The manifest records:

- target name
- start and end timestamps
- executed steps
- current Python executable

This is intentionally lightweight, but it gives the repository a basic operational run history.
