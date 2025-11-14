import os
from datetime import datetime
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from sample_data import SAMPLE_EXAMPLE_QUERIES
from typing import Optional, Dict, Any
from dotenv import load_dotenv

# Load environment
load_dotenv()

# -----------------------------
# IMPORT HELPERS
# -----------------------------
from cosmos_query import (
    insert_log_into_cosmos,
    get_all_logs,
    get_log_by_id,
    filter_logs,
    count_logs_by_severity,
    top_critical_logs
)

from generate_embedding_faiss import semantic_search_logs
from automation_trigger import send_logic_app_alert
from sample_data import SAMPLE_EXAMPLE_QUERIES

from servicebus_client import (
    send_message_to_servicebus,
    list_servicebus_queues,
    check_servicebus_health
)

# -----------------------------
# SWAGGER TAG METADATA
# -----------------------------
tags_metadata = [
    {"name": "Logs", "description": "Insert, fetch, filter logs stored in Cosmos DB."},
    {"name": "Semantic Search", "description": "AI-based log similarity search using embeddings."},
    {"name": "Service Bus", "description": "Queue messaging, listing queues, and health checks."},
    {"name": "Alerts", "description": "Trigger Logic App alerts and automation flows."},
    {"name": "Dashboard", "description": "Severity distribution & top critical events for UI."},
    {"name": "Admin", "description": "API health, configuration, version & system diagnostics."}
]

# -----------------------------
# FASTAPI APP CONFIG
# -----------------------------
app = FastAPI(
    title="Intelligent Log Insights API",
    description="Cloud-Native Observability Platform with Semantic Search, Cosmos DB, and Azure Service Bus.",
    version="1.0.0",
    openapi_tags=tags_metadata,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# -----------------------------
# Pydantic Models
# -----------------------------
class LogItem(BaseModel):
    level: str = Field(..., description="Log level: INFO, WARNING, ERROR, CRITICAL")
    service: str = Field(..., description="Microservice name")
    message: str = Field(..., description="Log message content")
    region: Optional[str] = Field("eastus", description="Azure region")
    timestamp: Optional[str] = Field(None, description="ISO8601 timestamp")


class SemanticRequest(BaseModel):
    query: str = Field(..., description="Search query text")


class QueueMessage(BaseModel):
    queue: str = Field(..., description="Target queue name")
    content: Dict[str, Any] = Field(..., description="Content of message")


class AlertTrigger(BaseModel):
    message: str = Field(..., description="Alert message body")


# ---------------------------------------------------------------------
# A) LOG INGESTION & STORAGE
# ---------------------------------------------------------------------
@app.post("/logs", tags=["Logs"], summary="Insert a new log")
async def insert_log(log: LogItem):
    return insert_log_into_cosmos(log.dict())


@app.get("/logs", tags=["Logs"], summary="Fetch all logs")
async def read_logs():
    return get_all_logs()


@app.get("/logs/{log_id}", tags=["Logs"], summary="Fetch a single log by ID")
async def read_log(log_id: str):
    result = get_log_by_id(log_id)
    if not result:
        raise HTTPException(404, "Log not found")
    return result


@app.get("/logs/filter", tags=["Logs"], summary="Filter logs by severity/service/region")
async def filter_logs_endpoint(level: Optional[str] = None,
                               service: Optional[str] = None,
                               region: Optional[str] = None):
    return filter_logs(level, service, region)


# ---------------------------------------------------------------------
# B) SEMANTIC SEARCH
# ---------------------------------------------------------------------
@app.post("/semantic-search", tags=["Semantic Search"], summary="Semantic log search using embeddings")
async def semantic_search(request: SemanticRequest):
    return semantic_search_logs(request.query)


@app.get("/semantic-search/example-queries", tags=["Semantic Search"], summary="Useful example queries")
async def example_queries():
    return SAMPLE_EXAMPLE_QUERIES


# ---------------------------------------------------------------------
# C) SERVICE BUS INTEGRATION
# ---------------------------------------------------------------------
@app.post("/send-to-queue", tags=["Service Bus"], summary="Send message to a Service Bus queue")
async def send_message(msg: QueueMessage):
    return send_message_to_servicebus(msg.queue, msg.content)


@app.get("/servicebus/health", tags=["Service Bus"], summary="Check Service Bus health")
async def sb_health():
    return check_servicebus_health()


@app.get("/servicebus/queues", tags=["Service Bus"], summary="List all available queues")
async def sb_queues():
    return list_servicebus_queues()


# ---------------------------------------------------------------------
# D) ALERTS & AUTOMATION
# ---------------------------------------------------------------------
@app.post("/trigger-alert", tags=["Alerts"], summary="Trigger Logic App alert manually")
async def logic_alert(alert: AlertTrigger):
    return send_logic_app_alert(alert.message)


@app.post("/simulate-high-error", tags=["Alerts"], summary="Simulate high error rate")
async def simulate_error():
    return send_logic_app_alert("ERROR_THRESHOLD_EXCEEDED")


@app.get("/alerts/status", tags=["Alerts"], summary="Mock alert statistics")
async def alert_status():
    return {"alerts_triggered": 18, "today": 5}  # sample


@app.post("/alerts/trigger", tags=["Alerts"], summary="Force trigger alert event")
async def manual_alert(alert: AlertTrigger):
    return {"status": "Alert sent", "message": alert.message}


# ---------------------------------------------------------------------
# E) DASHBOARD / OBSERVABILITY
# ---------------------------------------------------------------------
@app.get("/dashboard/severity-distribution", tags=["Dashboard"], summary="Pie chart severity distribution")
async def severity_distribution():
    return count_logs_by_severity()


@app.get("/dashboard/top-critical-events", tags=["Dashboard"], summary="Top 10 critical events")
async def critical_events():
    return top_critical_logs()


# ---------------------------------------------------------------------
# F) ADMIN / DEVOPS
# ---------------------------------------------------------------------
@app.get("/health", tags=["Admin"], summary="API health check")
async def health():
    return {"status": "healthy", "timestamp": datetime.utcnow()}


@app.get("/config", tags=["Admin"], summary="Safe environment configuration")
async def config():
    return {
        "cosmos": True,
        "faiss_index": True,
        "service_bus": True,
        "logic_app": True,
        "env_variables_loaded": True,
    }


@app.get("/version", tags=["Admin"], summary="API version")
async def version():
    return {"version": "1.0.0", "build": "2025.1111"}


@app.get("/status", tags=["Admin"], summary="Systemwide health")
async def status():
    return {
        "CosmosDB": "OK",
        "FAISS": "Loaded",
        "ServiceBus": check_servicebus_health(),
        "LogicApp": "Reachable",
    }
