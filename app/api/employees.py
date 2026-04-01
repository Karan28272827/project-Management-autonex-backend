from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from app.db.database import get_db
from app.models.allocation import Allocation
from app.models.employee import Employee
from app.models.leave import Leave
from app.models.side_project import SideProject
from app.models.user import User
from app.schemas.employee import (
    EmployeeCreate,
    EmployeeUpdate,
    EmployeeResponse,
)
from app.services.auth_service import hash_password

router = APIRouter(
    prefix="/api/employees",
    tags=["Employees"],
)

DEFAULT_EMPLOYEE_PASSWORD = "emp123"
DESIGNATION_ROLE_MAP = {
    "Admin": "admin",
    "Program Manager": "pm",
    "Annotator/ Reviewer": "employee",
    "Annotator/Reviewer": "employee",
    "Annotator": "employee",
    "Reviewer": "employee",
    "Developer": "employee",
}


def get_user_role_from_designation(designation: str | None) -> str:
    return DESIGNATION_ROLE_MAP.get(designation, "employee")


# ✅ CREATE EMPLOYEE
@router.post("", response_model=EmployeeResponse)
def create_employee(
    payload: EmployeeCreate,
    db: Session = Depends(get_db)
):
    # Check if email already exists
    existing = db.query(Employee).filter(Employee.email == payload.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    existing_user = db.query(User).filter(User.email == payload.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="User email already registered")
    
    employee = Employee(**payload.dict())
    db.add(employee)
    db.flush()

    user = User(
        email=employee.email,
        password_hash=hash_password(DEFAULT_EMPLOYEE_PASSWORD),
        name=employee.name,
        role=get_user_role_from_designation(employee.designation),
        employee_id=employee.id,
        skills=employee.skills or [],
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(employee)
    return employee


# ✅ LIST EMPLOYEES
@router.get("", response_model=list[EmployeeResponse])
def list_employees(
    status: str = None,
    db: Session = Depends(get_db)
):
    query = db.query(Employee)
    if status:
        query = query.filter(Employee.status == status)
    return query.all()


# ✅ GET EMPLOYEE BY ID
@router.get("/{employee_id}", response_model=EmployeeResponse)
def get_employee(
    employee_id: int,
    db: Session = Depends(get_db)
):
    employee = db.query(Employee).filter(Employee.id == employee_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    return employee


# ✅ UPDATE EMPLOYEE
@router.put("/{employee_id}", response_model=EmployeeResponse)
def update_employee(
    employee_id: int,
    payload: EmployeeUpdate,
    db: Session = Depends(get_db),
):
    employee = db.query(Employee).filter(Employee.id == employee_id).first()
    
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    # Check if email is being updated and if it's already taken
    if payload.email and payload.email != employee.email:
        existing = db.query(Employee).filter(Employee.email == payload.email).first()
        if existing:
            raise HTTPException(status_code=400, detail="Email already registered")
        existing_user = db.query(User).filter(User.email == payload.email).first()
        if existing_user:
            raise HTTPException(status_code=400, detail="User email already registered")
    
    for key, value in payload.dict(exclude_unset=True).items():
        setattr(employee, key, value)

    linked_user = db.query(User).filter(User.employee_id == employee.id).first()
    if linked_user:
        linked_user.email = employee.email
        linked_user.name = employee.name
        linked_user.role = get_user_role_from_designation(employee.designation)
        linked_user.skills = employee.skills or []
    
    db.commit()
    db.refresh(employee)
    return employee


# ✅ DELETE EMPLOYEE
@router.delete("/{employee_id}")
def delete_employee(
    employee_id: int,
    db: Session = Depends(get_db),
):
    employee = db.query(Employee).filter(Employee.id == employee_id).first()
    
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    try:
        db.query(Allocation).filter(Allocation.employee_id == employee.id).delete(synchronize_session=False)
        db.query(Leave).filter(Leave.employee_id == employee.id).delete(synchronize_session=False)
        db.query(SideProject).filter(SideProject.employee_id == employee.id).delete(synchronize_session=False)

        db.query(User).filter(User.employee_id == employee.id).delete(synchronize_session=False)
        db.flush()

        db.delete(employee)
        db.commit()
        return {"message": "Employee deleted successfully"}
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to delete employee and related records")
