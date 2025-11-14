def semantic_search_logs(query: str, top_k: int = 3):
    if not os.path.exists(INDEX_FILE):
        return {"error": "Index not found. Add logs first."}

    # Load saved index
    with open(INDEX_FILE, "r") as f:
        data = json.load(f)

    # Extract logs
    corpus_logs = [item["log"] for item in data]

    # Encode all logs again (embedding stored earlier but re-encoding allows tensor ops)
    corpus_embeddings = model.encode(corpus_logs, convert_to_tensor=True)

    # Encode query
    query_embedding = model.encode(query, convert_to_tensor=True)

    # Compute cosine similarity scores
    scores = util.cos_sim(query_embedding, corpus_embeddings)[0]

    # Pick top_k results
    top_results = scores.topk(top_k)

    results = []
    for score, idx in zip(top_results.values.tolist(), top_results.indices.tolist()):
        results.append({
            "log": corpus_logs[idx],
            "score": float(score)
        })

    return {
        "query": query,
        "results": results
    }
