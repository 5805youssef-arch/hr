from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from ..models.violation import Violation

PENALTY_MAP = {
    "Yellow": {"deduction_days": 0.0, "freeze_months": 0, "label": "Performance Notice"},
    "Orange": {"deduction_days": 0.5, "freeze_months": 0, "label": "Performance Flag — 0.5 Day Deduction"},
    "Red": {"deduction_days": 2.0, "freeze_months": 0, "label": "Performance Alert — 2 Days Deduction"},
    "Black": {"deduction_days": 4.0, "freeze_months": 3, "label": "Performance Warning — 4 Days + 3 Month Freeze"},
    "Investigation": {"deduction_days": 0.0, "freeze_months": 0, "label": "Suspended — Investigation"},
}

# We mirror the frontend rules here so the backend knows exactly how to escalate
RULES_MATRIX = {
    "Late Arrival": {"reset_days": 30, "esc": ["Yellow", "Yellow", "Orange", "Red", "Black", "Investigation"]},
    "No-Show": {"reset_days": 90, "esc": ["Red", "Red", "Black", "Investigation"]},
    "Exceed Breaks": {"reset_days": 30, "esc": ["Yellow", "Yellow", "Yellow", "Yellow", "Orange", "Red", "Black", "Investigation"]},
    "Early Leave": {"reset_days": 180, "esc": ["Black", "Investigation"]},
    "Abusive Words": {"reset_days": 180, "esc": ["Black", "Investigation"]},
    "Physical Harm": {"reset_days": 180, "esc": ["Investigation"]},
    "Sleeping on Job": {"reset_days": 180, "esc": ["Black", "Investigation"]},
    "Unprofessional": {"reset_days": 180, "esc": ["Black", "Investigation"]},
    "Company Assets": {"reset_days": 180, "esc": ["Investigation"]},
    "Routing Calls": {"reset_days": 180, "esc": ["Black", "Investigation"]},
    "Aux Abuse": {"reset_days": 30, "esc": ["Yellow", "Yellow", "Orange", "Red", "Black", "Investigation"]},
    "Mobile Phone": {"reset_days": 30, "esc": ["Red", "Black", "Investigation"]},
    "Food & Beverage": {"reset_days": 30, "esc": ["Orange", "Red", "Black", "Investigation"]},
    "Business Process": {"reset_days": 30, "esc": ["Orange", "Red", "Black", "Investigation"]},
    "Cyber Security": {"reset_days": 30, "esc": ["Red", "Black", "Investigation"]},
    "Harassment": {"reset_days": 180, "esc": ["Investigation"]},
    "Theft": {"reset_days": 180, "esc": ["Investigation"]},
}

def calculate_next_penalty(db: Session, employee_name: str, category: str, incident: str) -> str:
    # 1. Look up the rule for this incident (fallback to a standard 30-day rule if missing)
    rule = RULES_MATRIX.get(incident, {"reset_days": 30, "esc": ["Yellow", "Orange", "Red", "Black", "Investigation"]})
    
    # 2. Calculate the cutoff date for the reset window
    cutoff_date = datetime.utcnow() - timedelta(days=rule["reset_days"])
    
    # 3. Query the database: How many times has this employee done this in the time window?
    past_violations_count = db.query(Violation).filter(
        Violation.employee_name == employee_name,
        Violation.incident == incident,
        Violation.created_at >= cutoff_date
    ).count()
    
    # 4. Get the next penalty color based on the count
    esc_list = rule["esc"]
    
    # If they exceeded the max steps, they stay at the worst penalty (Investigation)
    if past_violations_count >= len(esc_list):
        return esc_list[-1]
        
    return esc_list[past_violations_count]

def build_penalty_label(penalty_color: str, applied_days: float) -> str:
    base = PENALTY_MAP.get(penalty_color, PENALTY_MAP["Yellow"])
    if applied_days != base["deduction_days"] and penalty_color != "Investigation":
        return f"{penalty_color} Card — {applied_days} Days Deduction (Override)"
    return base["label"]