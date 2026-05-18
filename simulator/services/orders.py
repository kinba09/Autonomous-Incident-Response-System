import random


def simulate_orders(latency_ms: int):
    if random.random() < 0.03:
        return 504, latency_ms + 300, "OrderTimeoutError"
    return 200, latency_ms, None
