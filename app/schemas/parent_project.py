from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date, datetime


class ParentProjectBase(BaseModel):
    """Base schema with common fields."""
    name: str = Field(..., min_length=2, description="Parent project name")
    program_manager_id: Optional[int] = Field(None, description="Employee ID of Program Manager")
    description: Optional[str] = Field(None, description="Scope of work")
    client: Optional[str] = Field(None, description="Client name for context inheritance")
    project_type: str = Field("Full", description="Project type: Full, POC, Side")
    global_start_date: date = Field(..., description="Project start date")
    tentative_duration_months: Optional[int] = Field(None, ge=1, description="Expected duration in months")
    status: Optional[str] = Field("active", description="Status: active, completed, archived")


class ParentProjectCreate(ParentProjectBase):
    """Schema for creating a new parent project."""
    program_manager_id: int = Field(..., description="Employee ID of Program Manager")


class ParentProjectUpdate(BaseModel):
    """Schema for updating a parent project - all fields optional."""
    name: Optional[str] = Field(None, min_length=2)
    program_manager_id: Optional[int] = None
    description: Optional[str] = None
    client: Optional[str] = None
    project_type: Optional[str] = None
    global_start_date: Optional[date] = None
    tentative_duration_months: Optional[int] = Field(None, ge=1)
    status: Optional[str] = None


class SubProjectSummary(BaseModel):
    """Lightweight sub-project info for parent project responses."""
    id: int
    name: str
    batch_name: Optional[str] = None
    project_status: str
    
    class Config:
        from_attributes = True


class ParentProjectResponse(ParentProjectBase):
    """Response schema with all fields including computed."""
    id: int
    created_at: datetime
    updated_at: datetime
    sub_projects_count: int = 0
    program_manager_name: Optional[str] = None  # Joined from Employee table
    
    class Config:
        from_attributes = True


class ParentProjectWithSubProjects(ParentProjectResponse):
    """Extended response including sub-project list."""
    sub_projects: List[SubProjectSummary] = []
