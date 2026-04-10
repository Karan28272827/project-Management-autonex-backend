from sqlalchemy import Column, Integer, String, Text, TIMESTAMP, ForeignKey, Index
from sqlalchemy.sql import func

from app.db.database import Base


class Referral(Base):
    __tablename__ = "referrals"

    id = Column(Integer, primary_key=True, index=True)

    # Who referred
    referrer_id = Column(Integer, ForeignKey("employees.id", ondelete="SET NULL"), nullable=True, index=True)

    # Candidate details
    candidate_name = Column(Text, nullable=False)
    candidate_email = Column(Text, nullable=False, index=True)
    candidate_phone = Column(String(32), nullable=True)
    candidate_linkedin = Column(Text, nullable=True)

    # Role they're being referred for
    position_applied = Column(Text, nullable=False)
    department = Column(Text, nullable=True)

    # How the referrer knows the candidate
    relationship = Column(Text, nullable=False)

    # Optional cover note from referrer
    note = Column(Text, nullable=True)

    # Lifecycle: pending → reviewing → interview_scheduled → hired | rejected
    status = Column(String(30), nullable=False, default="pending", index=True)

    # Set by admin when updating status
    status_note = Column(Text, nullable=True)

    created_at = Column(TIMESTAMP, server_default=func.now(), nullable=False)
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now(), nullable=False)

    __table_args__ = (
        Index("ix_referrals_referrer_status", "referrer_id", "status"),
    )
