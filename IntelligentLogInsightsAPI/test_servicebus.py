from azure.servicebus import ServiceBusClient, TransportType
from dotenv import load_dotenv
import os

load_dotenv()
conn_str = os.getenv("SERVICE_BUS_CONNECTION_STRING")

print("🔍 Loaded Connection String:", bool(conn_str))

try:
    # Create client using HTTPS transport (avoids AMQP firewall issues)
    client = ServiceBusClient.from_connection_string(
        conn_str,
        logging_enable=True,
        transport_type=TransportType.AmqpOverWebsocket
    )

    print("🔗 Connected successfully to namespace!")

    # Try sending and receiving test message to verify queues
    queue_name = "info-queue"  # Change if needed
    with client.get_queue_sender(queue_name) as sender:
        sender.send_messages("✅ Test message from Akshaya's client")
        print(f"📤 Test message sent to {queue_name}")

    print("✅ Service Bus connectivity and permissions confirmed!")

except Exception as e:
    print("❌ Failed to connect:", e)