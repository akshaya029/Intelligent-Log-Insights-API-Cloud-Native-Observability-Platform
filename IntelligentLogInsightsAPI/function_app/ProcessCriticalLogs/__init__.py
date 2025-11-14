import azure.functions as func
import json, logging, os
from azure.cosmos import CosmosClient, exceptions

def main(msg: func.ServiceBusMessage):
    try:
        data = json.loads(msg.get_body().decode('utf-8'))
        logging.info(f" [CRITICAL] Log received: {data}")

        client = CosmosClient.from_connection_string(os.environ["CosmosDBConnectionString"])
        db = client.get_database_client(os.environ["CosmosDBDatabase"])
        container = db.get_container_client(os.environ["CosmosDBContainer"])

        container.create_item(body=data)
        logging.info(f" Inserted CRITICAL log ID: {data.get('id')}")

    except exceptions.CosmosHttpResponseError as e:
        logging.error(f" Cosmos DB HTTP error: {e.message}")
    except Exception as ex:
        logging.error(f" Unexpected error (CriticalLogs): {str(ex)}")
