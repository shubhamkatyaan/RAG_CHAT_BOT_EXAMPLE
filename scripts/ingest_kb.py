# scripts/ingest_kb.py
import os
import glob
import pickle
from PyPDF2 import PdfReader
import numpy as np
from sentence_transformers import SentenceTransformer
from langchain.text_splitter import RecursiveCharacterTextSplitter
import faiss

# CONFIG
KB_DIR = "knowledge_base"
INDEX_DIR = os.path.join(KB_DIR, "index")
EMBED_MODEL = "all-MiniLM-L6-v2"  # small & fast
EMBED_DIM = 384  # dimension for all-MiniLM-L6-v2

# 1) Load or create index directory
os.makedirs(INDEX_DIR, exist_ok=True)
index_path = os.path.join(INDEX_DIR, "faiss_index.bin")
meta_path  = os.path.join(INDEX_DIR, "metadatas.pkl")

# 2) Read & chunk documents
documents = []
for ext in ("*.pdf", "*.txt"):
    for filepath in glob.glob(os.path.join(KB_DIR, ext)):
        text = ""
        if filepath.endswith(".pdf"):
            reader = PdfReader(filepath)
            for page in reader.pages:
                text += page.extract_text() or ""
        else:
            with open(filepath, "r", encoding="utf-8") as f:
                text = f.read()
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len
        )
        chunks = splitter.split_text(text)
        for i, chunk in enumerate(chunks):
            documents.append({
                "source": os.path.basename(filepath),
                "chunk_id": i,
                "text": chunk
            })

print(f"Total chunks: {len(documents)}")

# 3) Embed all chunks
model = SentenceTransformer(EMBED_MODEL)
texts = [doc["text"] for doc in documents]
embeddings = model.encode(texts, show_progress_bar=True)

# 4) Build FAISS index
index = faiss.IndexFlatL2(EMBED_DIM)
index.add(np.array(embeddings, dtype="float32"))

# 5) Persist index + metadata
faiss.write_index(index, index_path)
with open(meta_path, "wb") as f:
    pickle.dump(documents, f)

print("Indexing complete. Files written to:", INDEX_DIR)
