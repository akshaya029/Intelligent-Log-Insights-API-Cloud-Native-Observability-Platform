import os
from dotenv import load_dotenv
from azure.servicebus import ServiceBusClient, ServiceBusMessage

load_dotenv()

SERVICE_BUS_CONNECTION_STRING = os.getenv("SERVICE_BUS_CONNECTION_STRING")
SERVICE_BUS_NAMESPACE = os.getenv("SERVICE_BUS_NAMESPACE")

if not SERVICE_BUS_CONNECTION_STRING:
    raise ValueError("❌ Missing SERVICE_BUS_CONNECTION_STRING in .env")

# ---------------------------------------------------
# Initialize Service Bus Client
# ---------------------------------------------------
sb_client = ServiceBusClient.from_connection_string(
    conn_str=SERVICE_BUS_CONNECTION_STRING,
    logging_enable=True
)

# ---------------------------------------------------
# Send Message to Queue
# ---------------------------------------------------
def send_message_to_servicebus(queue_name: str, content: dict):
    try:
        sender = sb_client.get_queue_sender(queue_name)
        with sender:
            msg = ServiceBusMessage(str(content))
            sender.send_messages(msg)
        return {"status": "sent", "queue": queue_name, "content": content}

    except Exception as e:
        return {"error": str(e)}


# ---------------------------------------------------
# List Queues in Namespace
# ---------------------------------------------------
def list_servicebus_queues():
    try:
        admin = sb_client._connection.get_servicebus_management_client()
        queues = admin.list_queues()
        return {"queues": [q.name for q in queues]}
    except Exception as e:
        return {"error": str(e)}


# ---------------------------------------------------
# Check Namespace Health
# ---------------------------------------------------
def check_servicebus_health():
    try:
        admin = sb_client._connection.get_servicebus_management_client()
        list(admin.list_queues())
        return {"service_bus": "healthy", "namespace": SERVICE_BUS_NAMESPACE}
    except Exception as e:
        return {"service_bus": "unhealthy", "error": str(e)}
