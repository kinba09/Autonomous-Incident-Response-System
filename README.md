# Autonomous Incident Response System (Milestone A - Basic)

Basic incident simulator that generates:
- mock service behavior (`auth`, `payments`, `orders`)
- structured JSON logs
- simple alert events when 5xx error rate crosses a threshold

## Run (Local Python)

```bash
python3 simulator/main.py
```

## Run (Docker - OS Independent)

Build and run:

```bash
docker compose up --build
```

Run in background:

```bash
docker compose up --build -d
```

Stop:

```bash
docker compose down
```

## Outputs

- Logs: `data/logs/app.jsonl`
- Alerts: `data/incidents/alerts.jsonl`

The `data` folder is mounted into the container, so files are available on your host machine (Windows/macOS/Linux).

## Config (Optional)

You can tune behavior with env vars:
- `ITERATIONS` (default `600`)
- `SEED` (default `42`)
- `WINDOW_SECONDS` (default `20`)
- `ALERT_THRESHOLD` (default `0.30`)
- `ALERT_COOLDOWN_SECONDS` (default `30`)
- `TICK_SECONDS` (default `0.2`)

## Notes

- `payments` contains an intentional bug (`NullPointerPaymentMethod`) with elevated failures.
- Alert rule: `5xx_rate >= 30%` in a rolling window with cooldown.
- This is intentionally simple so you can plug in LangChain agents next.
