# from pydantic import BaseModel, Field
# from typing import List, Optional
# from datetime import date, datetime


# class ProjectBase(BaseModel):
#     name: str = Field(..., min_length=3)
#     client: str
#     project_type: str

#     total_tasks: int = Field(..., ge=0)
#     estimated_time_per_task: float = Field(..., gt=0)

#     required_expertise: List[str]
#     assigned_employee_ids: Optional[List[int]] = []  # NEW: Store assigned employee IDs

#     start_date: date
#     end_date: date

#     daily_target: Optional[int] = Field(0, ge=0)

#     project_duration_weeks: Optional[int]
#     project_duration_days: Optional[int]

#     priority: Optional[str] = "medium"


# class ProjectCreate(ProjectBase):
#     pass


# class ProjectUpdate(BaseModel):
#     name: Optional[str]
#     client: Optional[str]
#     project_type: Optional[str]

#     total_tasks: Optional[int]
#     estimated_time_per_task: Optional[float]

#     required_expertise: Optional[List[str]]
#     assigned_employee_ids: Optional[List[int]]  # NEW: Allow updating assigned employees

#     start_date: Optional[date]
#     end_date: Optional[date]

#     daily_target: Optional[int]

#     project_duration_weeks: Optional[int]
#     project_duration_days: Optional[int]

#     allocated_employees: Optional[int]

#     priority: Optional[str]
#     project_status: Optional[str]


# class ProjectResponse(ProjectBase):
#     id: int
#     allocated_employees: int
#     assigned_employee_ids: Optional[List[int]] = []  # NEW: Include in response
#     project_status: str

#     created_at: datetime
#     updated_at: datetime

#     class Config:
#         from_attributes = True

from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import date, datetime


class ProjectBase(BaseModel):
    name: str = Field(..., min_length=3)
    client: Optional[str] = ""  # Optional - sub-projects inherit from parent
    project_type: Optional[str] = "Full"

    total_tasks: int = Field(..., ge=0)
    estimated_time_per_task: float = Field(..., gt=0)

    required_expertise: List[str]
    assigned_employee_ids: Optional[List[int]] = []
    
    # NEW: Hierarchy fields
    main_project_id: Optional[int] = None
    batch_name: Optional[str] = None
    is_sub_project: Optional[bool] = False
    previous_sub_project_id: Optional[int] = None

    start_date: date
    end_date: date

    daily_target: Optional[int] = Field(0, ge=0)

    project_duration_weeks: Optional[int]
    project_duration_days: Optional[int]

    required_manpower: Optional[int] = 0  # Number of employees required
    allocated_employees: Optional[int] = 0  # Actual allocations (auto-updated)
    priority: Optional[str] = "medium"


class ProjectCreate(ProjectBase):
    pass


class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    client: Optional[str] = None
    project_type: Optional[str] = None

    total_tasks: Optional[int] = None
    estimated_time_per_task: Optional[float] = None

    required_expertise: Optional[List[str]] = None
    assigned_employee_ids: Optional[List[int]] = None
    
    # NEW: Hierarchy fields
    main_project_id: Optional[int] = None
    batch_name: Optional[str] = None
    is_sub_project: Optional[bool] = None
    previous_sub_project_id: Optional[int] = None

    start_date: Optional[date] = None
    end_date: Optional[date] = None

    daily_target: Optional[int] = None

    project_duration_weeks: Optional[int] = None
    project_duration_days: Optional[int] = None

    required_manpower: Optional[int] = None
    allocated_employees: Optional[int] = None

    priority: Optional[str] = None
    project_status: Optional[str] = None


class ProjectResponse(ProjectBase):
    id: int
    required_manpower: int = 0
    allocated_employees: int = 0
    project_status: str

    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
