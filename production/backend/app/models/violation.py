from sqlalchemy import Column, Integer, String, Float, DateTime, Text
from datetime import datetime
from ..db.base import Base

class Violation(Base):
    __tablename__ = "violations"
    
    id = Column(Integer, primary_key=True, index=True)
    employee_name = Column(String, nullable=False)
    category = Column(String, nullable=False)
    incident = Column(String, nullable=False)
    penalty_color = Column(String, nullable=False)
    penalty_label = Column(String, nullable=False)
    deduction_hours = Column(Float, default=0.0)
    deduction_days = Column(Float, default=0.0)
    freeze_months = Column(Integer, default=0)
    comment = Column(Text, default="")
    submitted_by = Column(String, nullable=False)
    proof_image = Column(Text, default="")  # base64
    created_at = Column(DateTime, default=datetime.utcnow)
