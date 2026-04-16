from pydantic import BaseModel
from typing import List, Optional

class RuleCreate(BaseModel):
    category: str
    incident: str
    description: Optional[str] = ""
    hr_note: Optional[str] = ""
    reset_days: int = 90
    escalation: List[str]

class RuleResponse(BaseModel):
    id: int
    category: str
    incident: str
    reset_days: int
    escalation: List[str]

    class Config:
        from_attributes = True
