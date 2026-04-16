from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class ViolationCreate(BaseModel):
    employee_name: str
    category: str
    incident: str
    submitted_by: str
    comment: Optional[str] = ""
    force_investigation: bool = False
    deduction_override: float = -1.0
    proof_image: Optional[str] = ""   # base64

class ViolationResponse(BaseModel):
    id: int
    employee_name: str
    category: str
    incident: str
    penalty_color: str
    penalty_label: str
    deduction_days: float
    freeze_months: int
    submitted_by: str
    created_at: datetime

    class Config:
        from_attributes = True
