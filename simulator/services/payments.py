import random


def simulate_payments(latency_ms: int):
    # Intentional bug: elevated failure rate.
    if random.random() < 0.35:
        return 500, latency_ms, "NullPointerPaymentMethod"
    return 200, latency_ms, None
