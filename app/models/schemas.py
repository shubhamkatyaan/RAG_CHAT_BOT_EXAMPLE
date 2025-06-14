from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Literal

class ComplaintCreate(BaseModel):
    name: str = Field(..., min_length=1)
    phone_number: str = Field(..., min_length=7, max_length=15)
    email: EmailStr
    complaint_details: str = Field(..., min_length=1)

class ComplaintResponse(BaseModel):
    complaint_id: str
    message: str

class ComplaintOut(BaseModel):
    complaint_id: str
    name: str
    phone_number: str
    email: EmailStr
    complaint_details: str
    created_at: datetime
    status: Literal["Pending", "In Progress", "Delayed", "Resolved"]  # ✅ added
