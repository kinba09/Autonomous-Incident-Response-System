import json
import os
import random
import time
import uuid
import sys
from collections import defaultdict, deque
from datetime import datetime, timezone
from pathlib import Path

ROOT_PATH = Path(__file__).resolve().parents[1]
if str(ROOT_PATH) not in sys.path:
    sys.path.insert(0, str(ROOT_PATH))

from simulator.services import SERVICE_HANDLERS, service_response

LOG_PATH = Path(os.getenv("LOG_PATH", "data/logs/app.jsonl"))
ALERT_PATH = Path(os.getenv("ALERT_PATH", "data/incidents/alerts.jsonl"))

SERVICES = list(SERVICE_HANDLERS.keys())
WINDOW_SECONDS = int(os.getenv("WINDOW_SECONDS", "20"))
ALERT_THRESHOLD = float(os.getenv("ALERT_THRESHOLD", "0.30"))
ALERT_COOLDOWN_SECONDS = int(os.getenv("ALERT_COOLDOWN_SECONDS", "30"))
TICK_SECONDS = float(os.getenv("TICK_SECONDS", "0.2"))
ITERATIONS = int(os.getenv("ITERATIONS", "20"))
SEED = int(os.getenv("SEED", "42"))


class RollingMetrics:
    def __init__(self, window_seconds: int):
        self.window_seconds = window_seconds
        self.events = defaultdict(deque)  # service -> deque[(ts, is_5xx, request_id)]

    def add(self, service: str, ts: float, is_5xx: bool, request_id: str):
        q = self.events[service]
        q.append((ts, is_5xx, request_id))
        self._trim(service, ts)

    def _trim(self, service: str, now_ts: float):
        q = self.events[service]
        cutoff = now_ts - self.window_seconds
        while q and q[0][0] < cutoff:
            q.popleft()

    def error_rate(self, service: str, now_ts: float):
        self._trim(service, now_ts)
        q = self.events[service]
        total = len(q)
        if total == 0:
            return 0.0, 0, []
        errors = sum(1 for _, is_5xx, _ in q if is_5xx)
        sample = [rid for _, is_5xx, rid in list(q)[-20:] if is_5xx][:5]
        return errors / total, total, sample


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def write_jsonl(path: Path, record: dict):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record) + "\n")


def main(iterations: int = ITERATIONS, seed: int = SEED):
    random.seed(seed)
    metrics = RollingMetrics(WINDOW_SECONDS)
    last_alert_at = {}  # service -> ts

    print("Starting basic incident simulator...")
    print(f"Logs: {LOG_PATH}")
    print(f"Alerts: {ALERT_PATH}")

    for _ in range(iterations):
        ts = time.time()
        service = random.choice(SERVICES)
        request_id = str(uuid.uuid4())
        status_code, latency_ms, error_type = service_response(service)

        log = {
            "timestamp": utc_now_iso(),
            "service": service,
            "level": "ERROR" if status_code >= 500 else "INFO",
            "request_id": request_id,
            "message": "request failed" if status_code >= 500 else "request success",
            "error_type": error_type,
            "stack_trace": "simulated stack trace" if status_code >= 500 else None,
            "latency_ms": latency_ms,
            "status_code": status_code,
        }
        write_jsonl(LOG_PATH, log)

        metrics.add(service, ts, status_code >= 500, request_id)
        rate, total, sample_ids = metrics.error_rate(service, ts)

        should_alert = total >= 10 and rate >= ALERT_THRESHOLD
        last = last_alert_at.get(service, 0)

        if should_alert and (ts - last) >= ALERT_COOLDOWN_SECONDS:
            incident = {
                "incident_id": f"inc_{uuid.uuid4().hex[:10]}",
                "triggered_at": utc_now_iso(),
                "service": service,
                "rule_id": "high_5xx_rate",
                "window_seconds": WINDOW_SECONDS,
                "error_rate": round(rate, 3),
                "sample_request_ids": sample_ids,
                "severity": "high" if rate >= 0.5 else "medium",
                "state": "OPEN",
            }
            write_jsonl(ALERT_PATH, incident)
            last_alert_at[service] = ts
            print(f"[ALERT] {service} 5xx rate={rate:.2%} over last {WINDOW_SECONDS}s")

        time.sleep(TICK_SECONDS)

    print("Simulation complete.")


if __name__ == "__main__":
    main()
