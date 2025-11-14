import logging
import json
import random
import time
import os
import base64
import hmac
import hashlib
import requests
from datetime import datetime
from dotenv import load_dotenv


# Step 1: Load environment variables
load_dotenv()
WORKSPACE_ID = os.getenv("WORKSPACE_ID")
SHARED_KEY = os.getenv("SHARED_KEY")
LOG_TYPE = os.getenv("LOG_TYPE", "CustomAppLogs")


# Step 2: Configure logging (console + file)
log_filename = f"app_logs_{datetime.now().strftime('%Y-%m-%d')}.log"

logging.basicConfig(
    filename=log_filename,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

console = logging.StreamHandler()
console.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
console.setFormatter(formatter)
logging.getLogger("").addHandler(console)


# Step 3: Build Azure signature (for authentication)
def build_signature(customer_id, shared_key, date, content_length, method, content_type, resource):
    x_headers = f"x-ms-date:{date}"
    string_to_hash = f"{method}\n{str(content_length)}\n{content_type}\n{x_headers}\n{resource}"
    bytes_to_hash = bytes(string_to_hash, encoding="utf-8")
    decoded_key = base64.b64decode(shared_key)
    encoded_hash = base64.b64encode(
        hmac.new(decoded_key, bytes_to_hash, hashlib.sha256).digest()
    ).decode()
    return f"SharedKey {customer_id}:{encoded_hash}"


# Step 4: Send batch of logs to Azure Log Analytics
def send_batch_to_log_analytics(batch):
    if not batch:
        return

    if not WORKSPACE_ID or not SHARED_KEY:
        print("⚠️ Workspace ID or Shared Key missing in .env file.")
        return

    body = json.dumps(batch)
    method = "POST"
    content_type = "application/json"
    resource = "/api/logs"
    rfc1123date = datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S GMT")
    content_length = len(body)

    signature = build_signature(WORKSPACE_ID, SHARED_KEY, rfc1123date, content_length, method, content_type, resource)
    uri = f"https://{WORKSPACE_ID}.ods.opinsights.azure.com{resource}?api-version=2016-04-01"

    headers = {
        "Content-Type": content_type,
        "Authorization": signature,
        "Log-Type": LOG_TYPE,
        "x-ms-date": rfc1123date
    }

    response = requests.post(uri, data=body, headers=headers)
    if 200 <= response.status_code <= 299:
        print(f" Sent {len(batch)} logs to Log Analytics.")
    else:
        print(f" Failed to send batch: {response.status_code} -> {response.text}")


# Step 5: Buffer system for batched sending
log_buffer = []
BATCH_SIZE = 10       # Number of logs before sending
BATCH_INTERVAL = 30   # Seconds between forced sends
last_send_time = time.time()

def log_json(level, message, service="auth-service", region="eastus"):
    global last_send_time, log_buffer

    log_entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "service": service,
        "level": level,
        "message": message,
        "region": region
    }

    # Save locally (for backup)
    with open("structured_logs.json", "a") as f:
        f.write(json.dumps(log_entry) + "\n")

    # Add to batch buffer
    log_buffer.append(log_entry)

    # Check if batch ready to send
    if len(log_buffer) >= BATCH_SIZE or (time.time() - last_send_time) >= BATCH_INTERVAL:
        send_batch_to_log_analytics(log_buffer)
        log_buffer = []
        last_send_time = time.time()


# Step 6: Generate random logs (with guaranteed alerts)
def generate_random_log():
    # Logs that trigger Azure Alerts
    trigger_logs = [
        {"level": "CRITICAL", "message": "Simulated critical failure"},
        {"level": "ERROR", "message": "Database connection lost"},
        {"level": "WARNING", "message": "Service latency warning"},
        {"level": "ERROR", "message": "Token validation failed for user TEST"}
    ]

    # Normal logs for mix
    normal_logs = [
        {"level": "INFO", "message": "User login successful"},
        {"level": "DEBUG", "message": "Cache refreshed successfully"},
        {"level": "INFO", "message": "Order processed successfully"}
    ]

    # Pick a log: 1 in 3 chance of triggering alert
    if random.randint(1, 3) == 1:
        log = random.choice(trigger_logs)
    else:
        log = random.choice(normal_logs)

    service = random.choice(["auth-service", "order-service", "payment-service", "user-service"])
    region = random.choice(["eastus", "westus", "centralus"])

    # Print to console and send
    getattr(logging, log["level"].lower())(f"[{service}] {log['message']}")
    log_json(log["level"], log["message"], service, region)


# Step 7: Continuous log generation
def start_log_generation():
    count = 0
    print("\n Log generation started... Press Ctrl + C to stop.\n")

    try:
        while True:
            generate_random_log()
            count += 1
            time.sleep(2)
    except KeyboardInterrupt:
        print(f"\n Log generation stopped manually. Total logs created: {count}\n")

        # Send any remaining logs
        if log_buffer:
            send_batch_to_log_analytics(log_buffer)
            print(f"Sent remaining {len(log_buffer)} logs before shutdown.")


# Run script
if __name__ == "__main__":
    start_log_generation()
