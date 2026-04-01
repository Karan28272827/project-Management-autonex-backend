from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class SkillBase(BaseModel):
    name: str


class SkillCreate(SkillBase):
    pass


class Skill(SkillBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True