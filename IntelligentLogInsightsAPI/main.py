from fastapi import FastAPI, Request
from azure.servicebus import ServiceBusClient, ServiceBusMessage
from dotenv import load_dotenv
import os
import json

# Load environment variables
load_dotenv()

app = FastAPI()

# Azure Service Bus connection string
SERVICE_BUS_CONNECTION_STR = os.getenv("SERVICE_BUS_CONNECTION_STR")

# Queue names
QUEUES = {
    "critical": "critical-alerts-queue",
    "error": "error-alerts-queue",
    "security": "security-alerts-queue",
    "performance": "performance-alerts-queue"
}


def send_to_queue(queue_name: str, payload: dict):
    """Helper function to send message to Service Bus queue"""
    with ServiceBusClient.from_connection_string(SERVICE_BUS_CONNECTION_STR) as client:
        sender = client.get_queue_sender(queue_name)
        with sender:
            msg = ServiceBusMessage(json.dumps(payload))
            sender.send_messages(msg)


@app.post("/log-alert")
async def receive_alert(request: Request):
    """Receives alerts from Log Analytics (Azure Monitor)"""
    body = await request.json()
    essentials = body.get("data", {}).get("essentials", {})
    alert_rule = essentials.get("alertRule", "").lower()

    payload = {
        "alertName": essentials.get("alertRule"),
        "severity": essentials.get("severity"),
        "description": essentials.get("description"),
        "firedTime": essentials.get("firedDateTime"),
        "monitorService": essentials.get("monitoringService")
    }

    # Routing logic
    if "critical" in alert_rule:
        send_to_queue(QUEUES["critical"], payload)
    elif "error" in alert_rule:
        send_to_queue(QUEUES["error"], payload)
    elif "security" in alert_rule:
        send_to_queue(QUEUES["security"], payload)
    elif "performance" in alert_rule:
        send_to_queue(QUEUES["performance"], payload)
    else:
        print("No matching alert type found.")

    return {"status": "Alert processed", "queue": alert_rule}
