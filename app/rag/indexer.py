# app/rag/indexer.py
import os, glob, pickle
from PyPDF2 import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np

KB_DIR = "knowledge_base"
INDEX_DIR = os.path.join(KB_DIR, "index")
INDEX_PATH = os.path.join(INDEX_DIR, "faiss_index.bin")
META_PATH  = os.path.join(INDEX_DIR, "metadatas.pkl")

EMBED_MODEL = "all-MiniLM-L6-v2"
EMBED_DIM = 384

def ingest_kb():
    os.makedirs(INDEX_DIR, exist_ok=True)
    # (repeat the same steps as in scripts/ingest_kb.py)
    # ...
    # after writing files:
    return INDEX_PATH, META_PATH

def load_index():
    index = faiss.read_index(INDEX_PATH)
    with open(META_PATH, "rb") as f:
        metadatas = pickle.load(f)
    return index, metadatas

def embed_texts(texts: list[str]) -> np.ndarray:
    model = SentenceTransformer(EMBED_MODEL)
    return model.encode(texts, show_progress_bar=False)
