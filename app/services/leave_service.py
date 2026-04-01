from typing import List
from app.schemas.leave import Leave, LeaveCreate, LeaveUpdate
from datetime import datetime

LEAVES_DB: List[Leave] = []

def create_leave(leave: LeaveCreate) -> Leave:
    leave_id = len(LEAVES_DB) + 1
    new_leave = Leave(
        leave_id=leave_id,
        **leave.dict(),
        created_at=datetime.utcnow().isoformat(),
        updated_at=datetime.utcnow().isoformat()
    )
    LEAVES_DB.append(new_leave)
    return new_leave

def list_leaves() -> List[Leave]:
    return LEAVES_DB
