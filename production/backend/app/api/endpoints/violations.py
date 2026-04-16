from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime
from ...db.session import get_db
from ...schemas.violation import ViolationCreate, ViolationResponse
from ...crud.violation import create_violation
from ...utils.penalty import calculate_next_penalty, build_penalty_label, PENALTY_MAP
from ...utils.email import send_violation_email

router = APIRouter()

@router.post("/", response_model=ViolationResponse)
def log_violation(v: ViolationCreate, db: Session = Depends(get_db)):
    penalty_color = "Investigation" if v.force_investigation else calculate_next_penalty(
        db, v.employee_name, v.category, v.incident
    )
    
    applied_days = v.deduction_override if v.deduction_override >= 0 else PENALTY_MAP[penalty_color]["deduction_days"]
    
    violation_data = {
        "employee_name": v.employee_name,
        "category": v.category,
        "incident": v.incident,
        "penalty_color": penalty_color,
        "penalty_label": build_penalty_label(penalty_color, applied_days),
        "deduction_days": applied_days,
        "freeze_months": PENALTY_MAP[penalty_color]["freeze_months"],
        "comment": v.comment or "",
        "submitted_by": v.submitted_by,
        "proof_image": v.proof_image or "",
        "created_at": datetime.utcnow()
    }
    
    created = create_violation(db, violation_data)

    # Send email
    send_violation_email(
        emp_email="employee@tg.sa",           # TODO: get from employee table later
        manager_email="manager@tg.sa",
        emp_name=v.employee_name,
        category=v.category,
        incident=v.incident,
        penalty_color=penalty_color,
        comment=v.comment or "",
        applied_days=applied_days,
        proof_b64=v.proof_image
    )

    return created
