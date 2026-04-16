from sqlalchemy import Column, Integer, String, Text
from ..db.base import Base
import json

class Rule(Base):
    __tablename__ = "rules"
    
    id = Column(Integer, primary_key=True, index=True)
    category = Column(String, nullable=False)
    incident = Column(String, nullable=False)
    description = Column(Text, default="")
    hr_note = Column(Text, default="")
    reset_days = Column(Integer, default=90)
    escalation_json = Column(Text, default="[]")  # JSON string
