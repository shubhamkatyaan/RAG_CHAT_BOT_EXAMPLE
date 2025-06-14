# app/main.py
from dotenv import load_dotenv
load_dotenv()    # now os.environ is populated from .env
from fastapi import FastAPI

from app.api.complaints import router as complaints_router
from app.chat.router    import router as chat_router
from app.rag.retriever  import retrieve
from app.rag.llm        import generate
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="RAG-Chatbot Complaint API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # 👈 frontend origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 1) Complaint API
app.include_router(complaints_router, prefix="/complaints", tags=["complaints"])

# 2) Chat endpoint (handles filing & status lookups)
app.include_router(chat_router, prefix="", tags=["chat"])

# 3) Health check
@app.get("/", tags=["health"])
async def root():
    return {"status": "ok", "message": "API is up"}

# 4) RAG‐only test (for internal debugging)
@app.get("/rag-test", tags=["rag"])
async def rag_test(q: str):
    ctx = retrieve(q)
    ans = generate(q, ctx)
    return {"query": q, "answer": ans, "contexts": ctx}
