from .utils.logger import log_event


def login(user):
    service_name = "auth-service"

    log_event("INFO", service_name, "Login attempt started")

    # Constant bug: always crashes regardless of input
    try:
        username = user["name"]
        log_event("INFO", service_name, "Login successful", {"user": username})
        return username
    except Exception as e:
        log_event(
            "ERROR",
            service_name,
            "Login failed: Unauthorized access attempt",
            {"error": str(e)}
        )
        raise