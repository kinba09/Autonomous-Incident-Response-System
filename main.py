from services.auth_service import login
from services.payment_service import process_payment
from services.order_service import process_order
from services.utils.alert_manager import read_logs, generate_alerts, save_alerts

def run_auth_scenario():
    print("Running auth scenario...")
    try:
        user = None  # This triggers the auth bug
        login(user)
    except Exception as e:
        print("Auth Service Error:", str(e))


def run_payment_scenario():
    print("\nRunning payment scenario...")
    amount = None  # invalid input to trigger the payment bug
    balance = 500

    try:
        result = process_payment(amount, balance)
        print("Payment result:", result)
    except Exception as e:
        print("Payment Service Error:", str(e))


def run_order_scenario():
    print("\nRunning order scenario...")
    order = {"item": "Laptop", "quantity": 1}

    try:
        result = process_order(order)
        print("Order result:", result)
    except Exception as e:
        print("Order Service Error:", str(e))

def run_alert_system():
    print("\nRunning alert system...")

    logs = read_logs()
    alerts = generate_alerts(logs)

    for alert in alerts:
        print("ALERT:", alert)

    save_alerts(alerts)

if __name__ == "__main__":
    run_auth_scenario()
    run_payment_scenario()
    run_order_scenario()
    run_alert_system()
    print("\nSimulation completed. Check data/logs/app.jsonl")
