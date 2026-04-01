from sqlalchemy.orm import Session
from app.models.employee import Employee
from app.schemas.employees import EmployeeCreate, EmployeeUpdate
from app.services import skill as skill_service


def create_employee(db: Session, employee: EmployeeCreate):
    """Create a new employee"""
    # Create skills if they don't exist
    if employee.skills:
        for skill_name in employee.skills:
            skill_service.create_skill_if_not_exists(db, skill_name)
    
    db_employee = Employee(**employee.dict())
    db.add(db_employee)
    db.commit()
    db.refresh(db_employee)
    return db_employee


def update_employee(db: Session, employee_id: int, employee: EmployeeUpdate):
    """Update an employee"""
    db_employee = db.query(Employee).filter(Employee.id == employee_id).first()
    if not db_employee:
        return None
    
    # Create skills if they don't exist
    if employee.skills is not None:  # Changed to check for None instead of just truthy
        for skill_name in employee.skills:
            skill_service.create_skill_if_not_exists(db, skill_name)
    
    for key, value in employee.dict(exclude_unset=True).items():
        setattr(db_employee, key, value)
    
    db.commit()
    db.refresh(db_employee)
    return db_employee


def get_employee(db: Session, employee_id: int):
    """Get a single employee by ID"""
    return db.query(Employee).filter(Employee.id == employee_id).first()


def get_all_employees(db: Session):
    """Get all employees"""
    return db.query(Employee).all()


def delete_employee(db: Session, employee_id: int):
    """Delete an employee"""
    db_employee = db.query(Employee).filter(Employee.id == employee_id).first()
    if not db_employee:
        return None
    
    db.delete(db_employee)
    db.commit()
    return db_employee