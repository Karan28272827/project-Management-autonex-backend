from sqlalchemy import Column, Integer, String, Text, JSON, TIMESTAMP
from sqlalchemy.sql import func
from app.db.database import Base


class SignupRequest(Base):
    __tablename__ = "signup_requests"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(Text, nullable=False)
    email = Column(Text, nullable=False, unique=True, index=True)
    phone = Column(String(20), nullable=True)
    designation = Column(Text, nullable=True)
    employee_type = Column(Text, nullable=False, default="Full-time")
    skills = Column(JSON, default=list)
    reason = Column(Text, nullable=True)
    status = Column(String(20), nullable=False, default="pending", index=True)
    reviewed_by = Column(Integer, nullable=True)
    reviewed_at = Column(TIMESTAMP, nullable=True)
    rejection_reason = Column(Text, nullable=True)

    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
