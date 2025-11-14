from datetime import datetime

# -----------------------------------------
# Example semantic search queries
# -----------------------------------------
SAMPLE_EXAMPLE_QUERIES = [
    "Find logs related to authentication failures",
    "Show me critical errors from payments service",
    "Logs where the user login failed",
    "High latency or timeout logs",
    "Order processing failures in any region"
]

# -----------------------------------------
# Simulated logs (as if they came from Cosmos DB)
# -----------------------------------------
logs = [
    {
        "id": "log1",
        "timestamp": str(datetime.now()),
        "level": "ERROR",
        "service": "auth-api",
        "message": "User authentication failed due to token timeout",
        "region": "eastus"
    },
    {
        "id": "log2",
        "timestamp": str(datetime.now()),
        "level": "WARNING",
        "service": "payment-api",
        "message": "Payment request took longer than expected",
        "region": "westus"
    },
    {
        "id": "log3",
        "timestamp": str(datetime.now()),
        "level": "INFO",
        "service": "user-api",
        "message": "User profile updated successfully",
        "region": "centralus"
    }
]
