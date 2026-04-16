from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ...db.session import get_db
from ...schemas.employee import EmployeeCreate, EmployeeResponse
from ...crud.employee import create_employee, get_employees, delete_employee

router = APIRouter()

@router.post("/", response_model=EmployeeResponse)
def api_create_employee(emp: EmployeeCreate, db: Session = Depends(get_db)):
    return create_employee(db, emp)

@router.get("/", response_model=list[EmployeeResponse])
def api_get_employees(db: Session = Depends(get_db)):
    return get_employees(db)

@router.delete("/{name}")
def api_delete_employee(name: str, db: Session = Depends(get_db)):
    delete_employee(db, name)
    return {"message": f"Employee {name} deleted"}
