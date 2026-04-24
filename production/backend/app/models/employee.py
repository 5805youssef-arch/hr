from sqlalchemy import Column, Integer, String
from ..db.base import Base

class Employee(Base):
    __tablename__ = "employees"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, nullable=False)
    department = Column(String, default="")
    manager_email = Column(String, default="")
