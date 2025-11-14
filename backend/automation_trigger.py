import requests

# Set your Logic App URL here
LOGIC_APP_URL = "https://prod-60.eastus.logic.azure.com:443/workflows/5a92b7bf76ea4d0e972042be959a464d/triggers/When_an_HTTP_request_is_received/paths/invoke?api-version=2016-10-01&sp=%2Ftriggers%2FWhen_an_HTTP_request_is_received%2Frun&sv=1.0&sig=YullIy5P-iD3ZFYVwLSTUjXEMRNsQFQoo_VZ6wyf8Ro"


def send_logic_app_alert(error_message: str):
    """
    Sends error message to Azure Logic App HTTP Trigger.
    """

    if LOGIC_APP_URL == "" or LOGIC_APP_URL.startswith("YOUR_"):
        print("⚠ Logic App URL missing in automation_trigger.py")
        return {"error": "Logic App URL not configured"}

    payload = {"error_message": error_message}

    try:
        response = requests.post(LOGIC_APP_URL, json=payload)
        return {
            "status": "sent",
            "logic_app_status": response.status_code
        }

    except Exception as ex:
        return {"error": str(ex)}
