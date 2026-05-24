import json
from pathlib import Path
from typing import Any


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return rows


def get_latest_alert() -> dict[str, Any] | None:
    alerts_path = _repo_root() / "data" / "logs" / "alerts.jsonl"
    alerts = _read_jsonl(alerts_path)
    return alerts[-1] if alerts else None


def get_logs_by_service(service: str, limit: int = 50) -> list[dict[str, Any]]:
    logs_path = _repo_root() / "data" / "logs" / "app.jsonl"
    logs = _read_jsonl(logs_path)
    filtered = [row for row in logs if row.get("service") == service]
    return filtered[-limit:]


def get_recent_errors(limit: int = 50) -> list[dict[str, Any]]:
    logs_path = _repo_root() / "data" / "logs" / "app.jsonl"
    logs = _read_jsonl(logs_path)
    errors = [row for row in logs if row.get("level") == "ERROR"]
    return errors[-limit:]
