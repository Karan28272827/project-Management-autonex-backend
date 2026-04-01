"""
Guideline model - Stores project guideline documents and text.
"""
from sqlalchemy import Column, ForeignKey, Integer, Text, TIMESTAMP
from sqlalchemy.sql import func

from app.db.database import Base


class Guideline(Base):
    __tablename__ = "guidelines"

    id = Column(Integer, primary_key=True, index=True)

    main_project_id = Column(Integer, ForeignKey("main_projects.id"), nullable=True)
    # The current sub-project UI is backed by the daily-sheet compatibility model,
    # so we keep this as an application-level integer link instead of a DB FK.
    sub_project_id = Column(Integer, nullable=True)

    title = Column(Text, nullable=False)
    content = Column(Text, nullable=True)
    file_name = Column(Text, nullable=True)
    file_url = Column(Text, nullable=True)
    uploaded_by = Column(Integer, nullable=True)

    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(
        TIMESTAMP,
        server_default=func.now(),
        onupdate=func.now()
    )
