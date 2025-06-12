# app/rag/retriever.py
import numpy as np
from app.rag.indexer import load_index, embed_texts

index, metadatas = load_index()

def retrieve(query: str, k: int = 4) -> list[dict]:
    # 1) embed the query
    q_emb = embed_texts([query])[0].astype("float32")
    # 2) search FAISS
    D, I = index.search(np.array([q_emb]), k)
    results = []
    for idx in I[0]:
        meta = metadatas[idx]
        results.append({
            "source": meta["source"],
            "chunk_id": meta["chunk_id"],
            "text": meta["text"]
        })
    return results
