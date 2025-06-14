from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Literal, Optional

class ComplaintCreate(BaseModel):
    name: str = Field(..., min_length=1)
    phone_number: str = Field(..., min_length=7, max_length=15)
    email: EmailStr
    complaint_details: str = Field(..., min_length=1)
    user_id: Optional[str] = None  # ✅ optional — backend usually sets it, but included just in case

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
    status: Literal["Pending", "In Progress", "Delayed", "Resolved"]
    user_id: Optional[str]  # ✅ needed for authorization checks
