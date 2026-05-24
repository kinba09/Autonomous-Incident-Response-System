import json
from datetime import datetime
from pathlib import Path


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def read_logs():
    logs = []
    app_log = _repo_root() / "data" / "logs" / "app.jsonl"
    if not app_log.exists():
        raise FileNotFoundError(f"Log file not found: {app_log}")

    with app_log.open("r", encoding="utf-8") as f:
        for line in f:
            logs.append(json.loads(line))
    return logs


def generate_alerts(logs):
    alerts = []

    for log in logs:
        service = log["service"]
        level = log["level"]
        message = log["message"]
        extra = log.get("extra", {})

        # Rule 1: Runtime errors (highest priority)
        if level == "ERROR":
            alerts.append({
                "timestamp": datetime.utcnow().isoformat(),
                "service": service,
                "type": "RUNTIME_ERROR",
                "severity": "HIGH",
                "message": message,
                "details": extra
            })
        # Rule 2: Invalid input detection
        elif "invalid input" in message.lower():
            alerts.append({
                "timestamp": datetime.utcnow().isoformat(),
                "service": service,
                "type": "INVALID_INPUT",
                "severity": "MEDIUM",
                "message": message,
                "details": extra
            })

        #  Rule 3: Dependency failure
        elif level == "UNAVAILABLE":
            alerts.append({
                "timestamp": datetime.utcnow().isoformat(),
                "service": service,
                "type": "DEPENDENCY_FAILURE",
                "severity": "CRITICAL",
                "message": message,
                "details": extra
            })

    return alerts


def save_alerts(alerts):
    alerts_log = _repo_root() / "data" / "logs" / "alerts.jsonl"
    alerts_log.parent.mkdir(parents=True, exist_ok=True)
    with alerts_log.open("a", encoding="utf-8") as f:
        for alert in alerts:
            f.write(json.dumps(alert) + "\n")