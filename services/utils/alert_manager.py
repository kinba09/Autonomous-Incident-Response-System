import json
import uuid
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


def _classify_alert(log):
    service = log["service"]
    level = log["level"]
    message = log["message"]
    extra = log.get("extra", {})

    alert_type = None
    severity = None

    if level == "ERROR":
        if "invalid input" in message.lower():
            alert_type = "INVALID_INPUT"
            severity = "MEDIUM"
        elif "inventory service" in message.lower() or "unavailable" in message.lower():
            alert_type = "DEPENDENCY_FAILURE"
            severity = "CRITICAL"
        else:
            alert_type = "RUNTIME_ERROR"
            severity = "HIGH"
    elif level == "WARN":
        alert_type = "BUSINESS_WARNING"
        severity = "LOW"

    if alert_type is None:
        return None

    return {
        "incident_id": f"inc_{uuid.uuid4().hex[:10]}",
        "timestamp": datetime.utcnow().isoformat(),
        "service": service,
        "alert_type": alert_type,
        "severity": severity,
        "message": message,
        "evidence": {
            "log_timestamp": log.get("timestamp"),
            "log_level": level,
            "extra": extra,
        },
    }


def generate_alerts(logs):
    alerts = []
    seen = set()

    for log in logs:
        alert = _classify_alert(log)
        if alert is None:
            continue

        dedupe_key = (alert["service"], alert["alert_type"], alert["message"])
        if dedupe_key in seen:
            continue

        seen.add(dedupe_key)
        alerts.append(alert)

    return alerts


def save_alerts(alerts):
    alerts_log = _repo_root() / "data" / "logs" / "alerts.jsonl"
    alerts_log.parent.mkdir(parents=True, exist_ok=True)
    with alerts_log.open("a", encoding="utf-8") as f:
        for alert in alerts:
            f.write(json.dumps(alert) + "\n")
