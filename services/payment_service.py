from .utils.logger import log_event


def process_payment(amount, balance):
    service_name = "payment-service"

    log_event(
        "INFO",
        service_name,
        "Payment initiated",
        {"amount": amount, "balance": balance}
    )

    if amount is None or balance is None:
        log_event(
            "ERROR",
            service_name,
            "Payment failed due to invalid input",
            {"amount": amount, "balance": balance}
        )
        raise TypeError("Invalid payment amount or balance")

    if amount > balance:
        log_event(
            "WARN",
            service_name,
            "Payment declined due to insufficient balance",
            {"amount": amount, "balance": balance}
        )
        return "Payment Failed"

    log_event(
        "INFO",
        service_name,
        "Payment marked successful",
        {"amount": amount, "balance": balance}
    )
    return "Payment Successful"
