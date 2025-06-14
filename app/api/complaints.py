from fastapi import APIRouter, HTTPException, Request
from datetime import datetime
import uuid
import random

from app.models.schemas import ComplaintCreate, ComplaintResponse, ComplaintOut
from app.db.mongo import complaints_coll

router = APIRouter()

STATUSES = ["Pending", "In Progress", "Delayed", "Resolved"]

@router.post("", response_model=ComplaintResponse)
async def create_complaint(payload: ComplaintCreate, request: Request):  # ✅ Add `request`
    comp_id = str(uuid.uuid4())

    user_id = request.headers.get("user-id")  # ✅ Extract user ID
    print(f"[CREATE] Received user ID: {user_id}")  # ✅ Debug

    if not user_id:
        raise HTTPException(status_code=400, detail="User ID is required in the headers.")

    doc = payload.dict()
    doc.update({
        "complaint_id": comp_id,
        "created_at": datetime.utcnow(),
        "status": random.choice(STATUSES),
        "user_id": user_id  # ✅ Save to DB
    })

    await complaints_coll.insert_one(doc)

    return ComplaintResponse(
        complaint_id=comp_id,
        message="Complaint created successfully"
    )

@router.get("/{complaint_id}", response_model=ComplaintOut)
async def read_complaint(complaint_id: str, request: Request):  # ✅ Add `request`
    user_id = request.headers.get("user-id")  # ✅ Extract user ID
    print(f"[READ] Request for complaint {complaint_id} from user ID: {user_id}")  # ✅ Debug

    doc = await complaints_coll.find_one({"complaint_id": complaint_id})
    if not doc:
        raise HTTPException(status_code=404, detail="Complaint not found")

    # ✅ Authorization check
    if doc.get("user_id") != user_id:
        raise HTTPException(status_code=403, detail="You are not authorized to view this complaint.")

    return ComplaintOut(**doc)
