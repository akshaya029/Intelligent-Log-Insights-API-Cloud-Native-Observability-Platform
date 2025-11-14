from sentence_transformers import SentenceTransformer, util
import json
import os
from typing import List

# Load embedding model
model = SentenceTransformer("all-MiniLM-L6-v2")

# JSON file to store embeddings and logs
INDEX_FILE = "log_embeddings.json"


# -----------------------------------------
# Save logs + store embeddings in JSON file
# -----------------------------------------
def save_logs_to_index(logs: List[str]):
    print("🔹 Generating local embeddings using SentenceTransformer...")

    # Generate embeddings (as tensors)
    embeddings = model.encode(logs, convert_to_tensor=True).tolist()

    # Prepare data
    data = [{"log": log, "embedding": emb} for log, emb in zip(logs, embeddings)]

    # Save to file
    with open(INDEX_FILE, "w") as f:
        json.dump(data, f, indent=4)

    print(f" Saved {len(logs)} logs to local index successfully!")


# -----------------------------------------
# Semantic search using cosine similarity
# -----------------------------------------
def semantic_search_logs(query: str, top_k: int = 3):

    if not os.path.exists(INDEX_FILE):
        return {"error": "❌ No log index found. Add logs first."}

    # Load stored logs and embeddings
    with open(INDEX_FILE, "r") as f:
        data = json.load(f)

    # Extract only logs
    corpus_logs = [item["log"] for item in data]

    # Re-encode logs (tensor needed for cosine similarity)
    corpus_embeddings = model.encode(corpus_logs, convert_to_tensor=True)

    # Encode query
    query_embedding = model.encode(query, convert_to_tensor=True)

    # Calculate similarity
    scores = util.cos_sim(query_embedding, corpus_embeddings)[0]

    # Get best matches
    top_results = scores.topk(top_k)

    results = []
    for score, idx in zip(top_results.values.tolist(), top_results.indices.tolist()):
        results.append({
            "log": corpus_logs[idx],
            "score": float(score)
        })

    return {"query": query, "results": results}
