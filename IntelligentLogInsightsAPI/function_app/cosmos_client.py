from azure.cosmos import CosmosClient, PartitionKey

COSMOS_ENDPOINT = "https://logginginsights.documents.azure.com:443/"
COSMOS_KEY = "yYzeB4zpegzyjiP7mwkyPX88YTIvGb7LgfQCjJKSh5LWBN47JLzpfZt97CdXiAtsdc0pUl712MsOACDbmAyeBA=="
COSMOS_DATABASE = "logdb"
COSMOS_CONTAINER = "anomalies"

# Initialize once — shared by all Functions
client = CosmosClient(COSMOS_ENDPOINT, credential=COSMOS_KEY)
database = client.create_database_if_not_exists(id=COSMOS_DATABASE)
container = database.create_container_if_not_exists(
    id=COSMOS_CONTAINER,
    partition_key=PartitionKey(path="/pk")
)
