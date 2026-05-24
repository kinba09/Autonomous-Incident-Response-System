from .utils.logger import log_event


def process_order(order):
    """
    Simulates an order service with a constant intentional bug
    """
    service_name = "order-service"

    log_event(
        "INFO",
        service_name,
        "Order processing started",
        {"order": order}
    )

    try:
        if order is None:
            log_event(
                "ERROR",
                service_name,
                "Order processing failed: missing order payload",
                {"order": order}
            )
            raise TypeError("Order payload is required")

        if order.get("item") == "Laptop":
            log_event(
                "ERROR",
                service_name,
                "Order processing failed due to inventory service error",
                {"order": order}
            )
            raise RuntimeError("Inventory service unavailable")

        log_event(
            "INFO",
            service_name,
            "Order accepted",
            {"order": order}
        )
        return "Order Accepted"

    except Exception as e:
        log_event(
            "ERROR",
            service_name,
            "Order processing failed",
            {"error": str(e)}
        )
        raise
