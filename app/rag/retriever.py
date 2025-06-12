import pickle
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer

# Paths to your persisted index & metadata
INDEX_PATH = "knowledge_base/index/faiss_index.bin"
META_PATH  = "knowledge_base/index/metadatas.pkl"
EMBED_MODEL = "all-MiniLM-L6-v2"

# Lazy‐load globals
_embedder = None
_index    = None
_metadatas= None

def _load_index():
    global _embedder, _index, _metadatas
    if _index is None:
        _embedder  = SentenceTransformer(EMBED_MODEL)
        _index     = faiss.read_index(INDEX_PATH)
        with open(META_PATH, "rb") as f:
            _metadatas = pickle.load(f)
    return _embedder, _index, _metadatas

def retrieve(query: str, k: int = 2) -> list[dict]:
    """
    Embed the query, search the FAISS index for top-k chunks,
    then filter to only those mentioning 'headquart'. If none match,
    return the original top-k.
    """
    embedder, index, metadatas = _load_index()
    # 1) Embed the query
    q_emb = embedder.encode([query])[0].astype("float32")
    # 2) Search in FAISS
    _, I = index.search(np.array([q_emb]), k)
    chunks = [metadatas[idx] for idx in I[0]]
    # 3) Post-filter for the keyword
    filtered = [c for c in chunks if "headquart" in c["text"].lower()]
    return filtered if filtered else chunks
