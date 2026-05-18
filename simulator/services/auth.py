import random


def login(user):
    """
    Simulates a login service with an intentional bug
    """
    return user["name"]


def simulate_auth(latency_ms: int):
    # Simulate a request with occasional missing user data.
    if random.random() < 0.15:
        user = None
    else:
        user = {"name": random.choice(["Alice", "Bob", "Carol"])}

    try:
        login(user)
    except Exception:
        return 500, latency_ms, "AuthTokenValidationError"

    return 200, latency_ms, None
