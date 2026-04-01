"""
SideProject model — Personal side projects for employees.
"""
from sqlalchemy import Column, Integer, Text, Date, TIMESTAMP
from sqlalchemy.sql import func
from app.db.database import Base


class SideProject(Base):
    __tablename__ = "side_projects"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, nullable=False)
    name = Column(Text, nullable=False)
    description = Column(Text, nullable=True)
    status = Column(Text, default="active")  # active, completed, paused
    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)

    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
