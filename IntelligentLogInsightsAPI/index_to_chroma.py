import chromadb
from chromadb.config import Settings
import json, os
from dotenv import load_dotenv

load_dotenv()
db_dir = os.getenv("VECTOR_DB_DIR", "./vectorstore")
client = chromadb.Client(Settings(chroma_db_impl="duckdb+parquet", persist_directory=db_dir))

collection = client.get_or_create_collection(name="logs")

with open("logs_with_embeddings.json", "r", encoding="utf-8") as f:
    logs = json.load(f)

ids = [log["id"] for log in logs]
texts = [log["message"] for log in logs]
metadatas = [{"level": log.get("level", ""), "region": log.get("region", ""), "timestamp": log.get("timestamp", "")} for log in logs]
embeddings = [log["embedding"] for log in logs]

collection.add(ids=ids, embeddings=embeddings, documents=texts, metadatas=metadatas)
client.persist()

print(f" Stored {len(logs)} logs in Chroma Vector DB")
