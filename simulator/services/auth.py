import random


def simulate_auth(latency_ms: int):
    if random.random() < 0.02:
        return 500, latency_ms, "AuthTokenValidationError"
    return 200, latency_ms, None
