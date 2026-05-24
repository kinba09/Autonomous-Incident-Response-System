import json
from datetime import datetime


def log_event(level, service, message, extra=None):
    log = {
        "timestamp": datetime.utcnow().isoformat(),
        "level": level,
        "service": service,
        "message": message,
        "extra": extra or {}
    }

    with open("data/logs/app.jsonl", "a") as f:
        f.write(json.dumps(log) + "\n")