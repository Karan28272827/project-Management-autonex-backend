from sqlalchemy import Column, Integer, String, Float, Text, TIMESTAMP, JSON
from sqlalchemy.sql import func

from app.db.database import Base


class Employee(Base):
    __tablename__ = "employees"

    id = Column(Integer, primary_key=True, index=True)
    
    name = Column(Text, nullable=False)
    email = Column(Text, nullable=False, unique=True)
    razorpay_email = Column(Text, nullable=True)
    phone = Column(String(32), nullable=True)
    employee_type = Column(Text, nullable=False)  # Full-time, Part-time, Intern, Contract
    
    # Designation: Program Manager, Annotator, Developer, QA, Reviewer
    designation = Column(Text, default="Annotator")
    
    working_hours_per_day = Column(Float, nullable=False, default=8.0)
    weekly_availability = Column(Float, nullable=False, default=40.0)
    
    # Store skills as JSON array: ["Python", "Data Analysis", ...]
    skills = Column(JSON, nullable=True)

    slack_user_id = Column(String(64), nullable=True)
    
    productivity_baseline = Column(Float, nullable=False, default=1.0)

    # Monthly base salary (CTC) — used for payroll calculation
    base_salary = Column(Float, nullable=True)

    status = Column(Text, default="active")  # active, inactive, on-leave
    
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(
        TIMESTAMP,
        server_default=func.now(),
        onupdate=func.now()
    )

