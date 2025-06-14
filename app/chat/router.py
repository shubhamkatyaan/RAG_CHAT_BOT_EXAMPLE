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
    status: str = None
    rag_answer: str = None

router = APIRouter()

@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(req: ChatRequest):
    user_id = req.user_id
    text = req.text.lower()

    # 1) Complaint lookup (status or full details)
    m = re.search(r"([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})", text)
    if m and "complaint" in text:
        complaint_id = m.group(1)
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"http://127.0.0.1:8000/complaints/{complaint_id}",
                headers={"user-id": user_id}  # ✅ send user ID for validation
            )

        if resp.status_code == 403:
            return ChatResponse(
                reply="🚫 You are not authorized to view this complaint.",
                complaint_id=complaint_id
            )

        if resp.status_code == 200:
            data = resp.json()
            status = data.get("status", "Pending")

            if any(word in text for word in ["status", "track", "progress", "update"]):
                return ChatResponse(
                    reply=f"The status of your complaint is: {status}",
                    complaint_id=complaint_id,
                    status=status
                )

            detail_msg = (
                f"🆔 Complaint ID: {data['complaint_id']}\n"
                f"📌 Status: {status}\n"
                f"👤 Name: {data['name']}\n"
                f"📞 Phone: {data['phone_number']}\n"
                f"📧 Email: {data['email']}\n"
                f"📝 Issue: {data['complaint_details']}\n"
                f"📅 Filed On: {data['created_at']}"
            )
            return ChatResponse(
                reply=detail_msg,
                complaint_id=complaint_id,
                status=status
            )

        else:
            raise HTTPException(status_code=404, detail="Complaint not found")

    # 2) Complaint creation flow
    reply, done, data = ConversationManager.handle_message(user_id, text)
    if reply and not done:
        return ChatResponse(reply=reply)
    if done:
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                "http://127.0.0.1:8000/complaints", json=data,
                headers={"user-id": user_id}  # ✅ Pass user-id to backend
            )
        if resp.status_code == 200:
            j = resp.json()
            return ChatResponse(
                reply=f"✅ Your complaint has been registered with ID: {j['complaint_id']}. We'll get back to you soon.",
                complaint_id=j['complaint_id']
            )
        raise HTTPException(status_code=500, detail="Failed to register complaint")

    # 3) General conversation fallback using RAG
    contexts = retrieve(text)
    rag_ans = generate(text, contexts)

    if not rag_ans or rag_ans.strip() == "":
        rag_ans = "I'm still learning. Can you rephrase or ask something else?"

    return ChatResponse(reply=rag_ans, rag_answer=rag_ans)
