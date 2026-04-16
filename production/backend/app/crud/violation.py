from sqlalchemy.orm import Session
from ..models.violation import Violation
from datetime import datetime

def create_violation(db: Session, violation_data: dict):
    db_viol = Violation(**violation_data)
    db.add(db_viol)
    db.commit()
    db.refresh(db_viol)
    return db_viol

def get_violations(db: Session, skip=0, limit=100):
    return db.query(Violation).order_by(Violation.created_at.desc()).offset(skip).limit(limit).all()
