from fastapi import APIRouter, HTTPException

from ..db import db
from ..schemas import Employee, EmployeeIn

router = APIRouter(prefix="/employees", tags=["employees"])


@router.get("", response_model=list[Employee])
def list_employees():
    with db() as conn:
        rows = conn.execute("SELECT * FROM employees ORDER BY name").fetchall()
        return [dict(r) for r in rows]


@router.post("", response_model=Employee, status_code=201)
def create_employee(payload: EmployeeIn):
    with db() as conn:
        try:
            cur = conn.execute(
                """INSERT INTO employees (name, email, department, manager_email)
                   VALUES (?, ?, ?, ?)
                   ON CONFLICT(name) DO UPDATE SET
                       email = excluded.email,
                       department = excluded.department,
                       manager_email = excluded.manager_email
                   RETURNING *""",
                (payload.name, payload.email, payload.department, payload.manager_email),
            )
            row = cur.fetchone()
            return dict(row)
        except Exception as e:
            raise HTTPException(400, str(e))


@router.delete("/{name}", status_code=204)
def delete_employee(name: str):
    with db() as conn:
        conn.execute("DELETE FROM employees WHERE name = ?", (name,))
