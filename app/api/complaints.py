from fastapi import APIRouter, HTTPException
from datetime import datetime
import uuid
import random

from app.models.schemas import ComplaintCreate, ComplaintResponse, ComplaintOut
from app.db.mongo import complaints_coll

router = APIRouter()

STATUSES = ["Pending", "In Progress", "Delayed", "Resolved"]

@router.post("", response_model=ComplaintResponse)
async def create_complaint(payload: ComplaintCreate):
    comp_id = str(uuid.uuid4())

    doc = payload.dict()
    doc.update({
        "complaint_id": comp_id,
        "created_at": datetime.utcnow(),
        "status": random.choice(STATUSES)
        # ✅ No user_id field
    })

    await complaints_coll.insert_one(doc)

    return ComplaintResponse(
        complaint_id=comp_id,
        message="Complaint created successfully"
    )

@router.get("/{complaint_id}", response_model=ComplaintOut)
async def read_complaint(complaint_id: str):
    doc = await complaints_coll.find_one({"complaint_id": complaint_id})
    if not doc:
        raise HTTPException(status_code=404, detail="Complaint not found")

    return ComplaintOut(**doc)  # ✅ No user check
