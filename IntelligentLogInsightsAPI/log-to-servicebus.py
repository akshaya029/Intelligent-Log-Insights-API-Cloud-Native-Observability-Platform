# import os
# from azure.identity import DefaultAzureCredential
# from azure.monitor.query import LogsQueryClient
# from azure.servicebus import ServiceBusClient, ServiceBusMessage
# from datetime import timedelta
# from dotenv import load_dotenv

# # -----------------------------
# # Step 1: Load environment vars
# # -----------------------------
# dotenv_path = os.path.join(os.getcwd(), ".env")
# print(f" Loading environment from: {dotenv_path}")
# load_dotenv(dotenv_path=dotenv_path)

# # Debug check
# LOG_WORKSPACE_ID = os.getenv("LOG_ANALYTICS_WORKSPACE_ID")
# SERVICE_BUS_CONN_STR = os.getenv("SERVICE_BUS_CONNECTION_STRING")

# print(f" LOG_ANALYTICS_WORKSPACE_ID: {LOG_WORKSPACE_ID}")
# print(f" SERVICE_BUS_CONNECTION_STRING: {bool(SERVICE_BUS_CONN_STR)}")  # prints True if loaded

# if not LOG_WORKSPACE_ID:
#     raise ValueError(" LOG_ANALYTICS_WORKSPACE_ID is missing! Check your .env file name or location.")
# if not SERVICE_BUS_CONN_STR:
#     raise ValueError(" SERVICE_BUS_CONNECTION_STRING is missing! Check .env spelling.")

# # -----------------------------
# # Step 2: Define Queues
# # -----------------------------
# QUEUES = {

#     "error": "error-alerts-queue",
#     "critical": "critical-alerts-queue"
# }

# # -----------------------------
# # Step 3: Initialize Clients
# # -----------------------------
# print("🔗 Connecting to Azure...")
# credential = DefaultAzureCredential()
# logs_client = LogsQueryClient(credential)
# servicebus_client = ServiceBusClient.from_connection_string(SERVICE_BUS_CONN_STR)

# # -----------------------------
# # Step 4: KQL Query
# # -----------------------------
# query = """
# CustomAppLogs_CL
# | where TimeGenerated > ago(1h)
# | project TimeGenerated, Level, Message, service_s, region_s
# """


# print(" Running Log Analytics Query...")
# response = logs_client.query_workspace(
#     workspace_id=LOG_WORKSPACE_ID,
#     query=query,
#     timespan=timedelta(minutes=10)
# )

# # -----------------------------
# # Step 5: Send logs to Service Bus
# # -----------------------------
# if not response.tables:
#     print(" No results returned from Log Analytics.")
# else:
#     print(f" Retrieved {len(response.tables[0].rows)} rows from Log Analytics.")

#     for table in response.tables:
#         for row in table.rows:
#             log_time, severity, message, service, region = row
#             severity = str(severity).lower()
#             queue_name = QUEUES.get(severity, "info-queue")

#             log_message = f"[{severity.upper()}] {message} at {log_time}"
#             print(f" Sending to {queue_name}: {log_message}")

#             with servicebus_client.get_queue_sender(queue_name) as sender:
#                 msg = ServiceBusMessage(log_message)
#                 sender.send_messages(msg)

# print(" All logs processed successfully.")






import os
import json
import uuid
import logging
from datetime import timedelta
from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.monitor.query import LogsQueryClient
from azure.servicebus import ServiceBusClient, ServiceBusMessage
from azure.servicebus.management import ServiceBusAdministrationClient

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")

# Load environment variables
load_dotenv()
LOG_WORKSPACE_ID = os.getenv("LOG_ANALYTICS_WORKSPACE_ID")
SERVICE_BUS_CONN_STR = os.getenv("SERVICE_BUS_CONNECTION_STRING")

# Queues mapping
QUEUES = {
    "error": "error-alerts-queue",
    "critical": "critical-alerts-queue",
    "security": "security-alerts-queue",
    "performance": "performance-alerts-queue"
}

# Initialize Azure clients
credential = DefaultAzureCredential()
logs_client = LogsQueryClient(credential)
servicebus_client = ServiceBusClient.from_connection_string(SERVICE_BUS_CONN_STR)
admin_client = ServiceBusAdministrationClient.from_connection_string(SERVICE_BUS_CONN_STR)

# Verify queues
existing = [q.name for q in admin_client.list_queues()]
for q in QUEUES.values():
    if q not in existing:
        admin_client.create_queue(q)
        logging.info(f"Created missing queue: {q}")

# Query logs
query = """
CustomAppLogs_CL
| where TimeGenerated > ago(1h)
| project TimeGenerated, Level, Message, service_s, region_s
"""

response = logs_client.query_workspace(
    workspace_id=LOG_WORKSPACE_ID,
    query=query,
    timespan=timedelta(minutes=30)
)

# Send logs
if not response.tables:
    logging.warning("⚠️ No results found.")
else:
    for table in response.tables:
        for row in table.rows:
            log_time, level, message, service, region = row
            level = str(level).lower()

            queue_name = QUEUES.get(level)
            if not queue_name:
                continue

            # ✅ Make sure each payload has id + level (partition key)
            log_payload = {
                "id": str(uuid.uuid4()),
                "level": level.upper(),
                "message": message,
                "service": service or "UnknownService",
                "region": region or "UnknownRegion",
                "timestamp": str(log_time)
            }

            log_json = json.dumps(log_payload)
            logging.info(f"📤 Sending to {queue_name}: {log_json}")

            with servicebus_client.get_queue_sender(queue_name) as sender:
                sender.send_messages(ServiceBusMessage(log_json))

    logging.info("🎯 All logs sent successfully.")
