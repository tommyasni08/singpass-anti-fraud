# Data Layer

This folder contains the shared data layer for the Singpass anti-fraud portfolio.

## Structure

- `data_generator/`: Python generator code and config
- `input_data/raw/`: reserved for source files or reference inputs if needed later
- `input_data/generated/`: generated synthetic output tables

## Current generator entrypoint

The supported generator entrypoint is:

```bash
python3 data/data_generator/src/generate_dataset.py
```

This command generates the full shared synthetic dataset in one run:

- `users.csv`
- `devices.csv`
- `user_devices.csv`
- `services.csv`
- `sessions.csv`
- `session_context.csv`
- `events.csv`
- `fraud_labels.csv`

Output location:

```text
data/input_data/generated/
```

## How to run

From the repository root:

```bash
cd singpass-anti-fraud
python3 data/data_generator/src/generate_dataset.py
```

From inside the `data/` folder:

```bash
cd singpass-anti-fraud/data
python3 data_generator/src/generate_dataset.py
```

Using the helper shell script:

```bash
cd singpass-anti-fraud
./data/generate_synthetic_data.sh
```

## About running scripts one by one

The files under `data_generator/src/` such as `generate_entities.py`, `generate_sessions.py`, and `generate_events.py` are currently generator modules, not standalone CLI scripts.

The intended way to generate data is to run `generate_dataset.py`, which orchestrates:

1. entity generation
2. session generation
3. event generation
4. fraud-label generation

If later you want true step-by-step execution, we can add separate CLI entrypoints for each stage. That is not necessary for the current project.

## Config

Generator settings currently live in:

```text
data/data_generator/config/generator_config.json
```

This file controls the synthetic population size, session volume, and scenario weights used by the generator.
