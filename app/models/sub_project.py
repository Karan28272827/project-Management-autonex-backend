"""
SubProject model — NEW intermediate level in the project hierarchy.
Hierarchy: MainProject → SubProject → DailySheet → Allocations

SubProject has: name, client (auto-filled from parent), PM, description,
start_date, duration, status, and support for uploading guideline documents.
"""
from sqlalchemy import Column, Integer, String, Date, Text, TIMESTAMP, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.db.database import Base


class SubProject(Base):
    __tablename__ = "sub_projects"

    id = Column(Integer, primary_key=True, index=True)

    # Parent main project
    main_project_id = Column(Integer, ForeignKey("main_projects.id"), nullable=False)

    name = Column(Text, nullable=False)
    client = Column(Text, nullable=True)           # Auto-filled from parent MainProject
    pm_id = Column(Integer, nullable=True)          # Employee ID of assigned PM
    description = Column(Text, nullable=True)

    start_date = Column(Date, nullable=True)
    duration_days = Column(Integer, nullable=True)
    status = Column(Text, default="active")         # active, completed, on-hold, archived

    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(
        TIMESTAMP,
        server_default=func.now(),
        onupdate=func.now()
    )

    # Relationships
    main_project = relationship("MainProject", back_populates="sub_projects", foreign_keys=[main_project_id])
    daily_sheets = relationship("DailySheet", back_populates="sub_project", foreign_keys="DailySheet.sub_project_id")
