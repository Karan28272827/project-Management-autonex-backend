from typing import List
from app.schemas.allocation import Allocation, AllocationCreate, AllocationUpdate
from datetime import datetime

ALLOCATIONS_DB: List[Allocation] = []

def create_allocation(allocation: AllocationCreate) -> Allocation:
    allocation_id = len(ALLOCATIONS_DB) + 1
    new_allocation = Allocation(
        allocation_id=allocation_id,
        **allocation.dict(),
        created_at=datetime.utcnow().isoformat(),
        updated_at=datetime.utcnow().isoformat()
    )
    ALLOCATIONS_DB.append(new_allocation)
    return new_allocation

def list_allocations() -> List[Allocation]:
    return ALLOCATIONS_DB
