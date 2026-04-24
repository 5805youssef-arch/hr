from sqlalchemy.orm import Session
from ..models.employee import Employee
from ..schemas.employee import EmployeeCreate

def create_employee(db: Session, emp: EmployeeCreate):
    db_emp = Employee(**emp.dict())
    db.add(db_emp)
    db.commit()
    db.refresh(db_emp)
    return db_emp

def get_employees(db: Session):
    return db.query(Employee).all()

def delete_employee(db: Session, name: str):
    return db.query(Employee).filter(Employee.name == name).delete()
