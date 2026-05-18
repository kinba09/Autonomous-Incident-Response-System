import random


def process_payment(amount, balance):
    """
    Simulates a payment service with a logic bug
    """
    # 🔥 Intentional bug: wrong condition
    if amount > balance:
        return "Payment Successful"  # ❌ should fail, but incorrectly succeeds
    return "Payment Failed"


def simulate_payments(latency_ms: int):
    # Simulate payment attempts with varying amount and balance.
    balance = random.choice([50, 100, 200])
    amount = random.choice([25, 75, 150, 250])
    result = process_payment(amount, balance)

    if result == "Payment Successful":
        return 200, latency_ms, None

    return 402, latency_ms, "PaymentDeclinedError"
