import random

from simulator.services.auth import simulate_auth
from simulator.services.orders import simulate_orders
from simulator.services.payments import simulate_payments


SERVICE_HANDLERS = {
    "auth": simulate_auth,
    "orders": simulate_orders,
    "payments": simulate_payments,
}


def service_response(service: str):
    latency_ms = random.randint(40, 250)
    handler = SERVICE_HANDLERS.get(service)
    if handler is None:
        return 200, latency_ms, None
    return handler(latency_ms)
