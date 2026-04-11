from __future__ import annotations

import csv
import random
from datetime import datetime
from pathlib import Path
import sys

if __package__ in {None, ""}:
    sys.path.append(str(Path(__file__).resolve().parent.parent))
    from src.config import load_config
    from src.generate_entities import generate_devices_and_links, generate_services, generate_users
    from src.generate_events import generate_events_and_labels
    from src.generate_sessions import generate_sessions
else:
    from .config import load_config
    from .generate_entities import generate_devices_and_links, generate_services, generate_users
    from .generate_events import generate_events_and_labels
    from .generate_sessions import generate_sessions


def _write_csv(rows: list[dict], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        output_path.write_text("")
        return
    with output_path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    config = load_config(root / "config" / "generator_config.json")
    random.seed(config.random_seed)
    base_time = datetime(2026, 4, 11, 12, 0, 0)

    users = generate_users(config, base_time)
    devices, user_devices = generate_devices_and_links(config, users, base_time)
    services = generate_services(config)
    sessions, session_context = generate_sessions(config, users, user_devices, services, base_time)
    user_map = {row["user_id"]: row for row in users}
    events, fraud_labels = generate_events_and_labels(sessions, session_context, user_map)

    output_dir = root.parent / "input_data" / "generated"
    _write_csv(users, output_dir / "users.csv")
    _write_csv(devices, output_dir / "devices.csv")
    _write_csv(user_devices, output_dir / "user_devices.csv")
    _write_csv(services, output_dir / "services.csv")
    _write_csv(sessions, output_dir / "sessions.csv")
    _write_csv(session_context, output_dir / "session_context.csv")
    _write_csv(events, output_dir / "events.csv")
    _write_csv(fraud_labels, output_dir / "fraud_labels.csv")

    print(f"Generated reference tables, sessions, events, and labels in {output_dir}")


if __name__ == "__main__":
    main()
