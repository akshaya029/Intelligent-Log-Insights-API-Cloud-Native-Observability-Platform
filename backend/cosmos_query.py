import os
from dotenv import load_dotenv
from azure.cosmos import CosmosClient, exceptions

# ---------------------------------------------------
# Load Environment Variables
# ---------------------------------------------------
load_dotenv()

COSMOS_URI = os.getenv("COSMOS_URI")
COSMOS_KEY = os.getenv("COSMOS_KEY")
DATABASE_NAME = os.getenv("COSMOS_DB")
CONTAINER_NAME = os.getenv("COSMOS_CONTAINER")

if not COSMOS_URI or not COSMOS_KEY:
    raise ValueError(" CosmosDB credentials missing. Check .env file.")

# ---------------------------------------------------
# Cosmos DB Client Initialization
# ---------------------------------------------------
client = CosmosClient(COSMOS_URI, COSMOS_KEY)
database = client.get_database_client(DATABASE_NAME)
container = database.get_container_client(CONTAINER_NAME)

# ---------------------------------------------------
# Insert Log
# ---------------------------------------------------
def insert_log_into_cosmos(log: dict):
    log["id"] = log.get("id") or log["timestamp"]  # or generate UUID
    container.create_item(log)
    return {"status": "inserted", "log": log}

# ---------------------------------------------------
# Fetch All Logs
# ---------------------------------------------------
def get_all_logs():
    query = "SELECT * FROM c"
    items = list(container.query_items(query, enable_cross_partition_query=True))
    return items

# ---------------------------------------------------
# Fetch Single Log
# ---------------------------------------------------
def get_log_by_id(log_id: str):
    query = f"SELECT * FROM c WHERE c.id = '{log_id}'"
    items = list(container.query_items(query, enable_cross_partition_query=True))
    return items[0] if items else None

# ---------------------------------------------------
# Filter Logs by severity/service/region
# ---------------------------------------------------
def filter_logs(level=None, service=None, region=None):
    query = "SELECT * FROM c WHERE 1=1"

    if level:
        query += f" AND c.level = '{level.upper()}'"
    if service:
        query += f" AND c.service = '{service}'"
    if region:
        query += f" AND c.region = '{region}'"

    items = list(container.query_items(query, enable_cross_partition_query=True))
    return items

# ---------------------------------------------------
# Pie Chart Distribution by Severity
# ---------------------------------------------------
def count_logs_by_severity():
    query = """
    SELECT c.level, COUNT(1) AS count 
    FROM c 
    GROUP BY c.level
    """
    items = list(container.query_items(query, enable_cross_partition_query=True))
    return {"distribution": items}

# ---------------------------------------------------
# Top 10 Critical Events
# ---------------------------------------------------
def top_critical_logs():
    query = """
    SELECT TOP 10 * 
    FROM c 
    WHERE c.level = 'CRITICAL'
    ORDER BY c.timestamp DESC
    """
    items = list(container.query_items(query, enable_cross_partition_query=True))
    return items
