FROM python:3.11-slim

WORKDIR /app

COPY simulator ./simulator
COPY data ./data

ENV ITERATIONS=600
ENV SEED=42
ENV WINDOW_SECONDS=20
ENV ALERT_THRESHOLD=0.30
ENV ALERT_COOLDOWN_SECONDS=30
ENV TICK_SECONDS=0.2
ENV LOG_PATH=data/logs/app.jsonl
ENV ALERT_PATH=data/incidents/alerts.jsonl

CMD ["python", "simulator/main.py"]
