from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import httpx
import re

from app.chat.manager import ConversationManager
from app.rag.retriever import retrieve
from app.rag.llm import generate

# Chat endpoint schema
class ChatRequest(BaseModel):
    user_id: str
    text: str

class ChatResponse(BaseModel):
    reply: str = None
    complaint_id: str = None
    status: dict = None
    rag_answer: str = None

router = APIRouter()

@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(req: ChatRequest):
    user_id = req.user_id
    text = req.text

    # 1) Check for complaint status lookup
    m = re.search(r"complaint\s+([0-9a-fA-F\-]{36})", text)
    if m:
        cid = m.group(1)
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"http://127.0.0.1:8000/complaints/{cid}")
        if resp.status_code == 200:
            data = resp.json()
            # Format the response
            detail_msg = (
                f"Complaint ID: {data['complaint_id']}\n"
                f"Name: {data['name']}\n"
                f"Phone: {data['phone_number']}\n"
                f"Email: {data['email']}\n"
                f"Details: {data['complaint_details']}\n"
                f"Created At: {data['created_at']}"
            )
            return ChatResponse(reply=detail_msg, status=data)
        else:
            raise HTTPException(status_code=404, detail="Complaint not found")

    # 2) Handle complaint creation flow
    reply, done, data = ConversationManager.handle_message(user_id, text)
    if reply and not done:
        return ChatResponse(reply=reply)
    if done:
        # All fields collected: create complaint
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                "http://127.0.0.1:8000/complaints", json=data
            )
        if resp.status_code == 200:
            j = resp.json()
            return ChatResponse(
                reply=f"Your complaint has been registered with ID: {j['complaint_id']}. We'll get back to you soon.",
                complaint_id=j['complaint_id']
            )
        raise HTTPException(status_code=500, detail="Failed to register complaint")

    # 3) Fallback to RAG-based response
    contexts = retrieve(text)
    rag_ans = generate(text, contexts)
    return ChatResponse(reply=rag_ans, rag_answer=rag_ans)
