import random


def process_order(order):
    """
    Simulates an order service with a logic bug
    """
    #  Intentional bug: wrong condition
    if order["quantity"] <= 0:
        return "Order Accepted"  # should fail for invalid quantity
    return "Order Failed"


def simulate_orders(latency_ms: int):
    order = {
        "item": random.choice(["widget", "gadget", "thing"]),
        "quantity": random.choice([-1, 0, 1, 2, 3]),
    }
    result = process_order(order)

    if result == "Order Accepted":
        return 200, latency_ms, None

    return 400, latency_ms, "OrderValidationError"
