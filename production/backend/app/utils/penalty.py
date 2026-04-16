from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from ..models.violation import Violation
import json

PENALTY_MAP = {
    "Yellow": {"deduction_days": 0.0, "freeze_months": 0, "label": "Performance Notice"},
    "Orange": {"deduction_days": 0.5, "freeze_months": 0, "label": "Performance Flag — 0.5 Day Deduction"},
    "Red": {"deduction_days": 2.0, "freeze_months": 0, "label": "Performance Alert — 2 Days Deduction"},
    "Black": {"deduction_days": 4.0, "freeze_months": 3, "label": "Performance Warning — 4 Days + 3 Month Freeze"},
    "Investigation": {"deduction_days": 0.0, "freeze_months": 0, "label": "Suspended — Investigation"},
}

def calculate_next_penalty(db: Session, employee_name: str, category: str, incident: str) -> str:
    # TODO: Later connect to Rules table for dynamic escalation
    return "Yellow"   # Default for now

def build_penalty_label(penalty_color: str, applied_days: float) -> str:
    base = PENALTY_MAP.get(penalty_color, PENALTY_MAP["Yellow"])
    if applied_days != base["deduction_days"] and penalty_color != "Investigation":
        return f"{penalty_color} Card — {applied_days} Days Deduction (Override)"
    return base["label"]
