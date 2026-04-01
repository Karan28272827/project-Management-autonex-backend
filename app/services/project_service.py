from typing import List
from app.schemas.project import Project, ProjectCreate

PROJECTS_DB: List[Project] = []


def create_project(project: ProjectCreate) -> Project:
    project_id = len(PROJECTS_DB) + 1
    new_project = Project(id=project_id, **project.dict())
    PROJECTS_DB.append(new_project)
    return new_project


def list_projects() -> List[Project]:
    return PROJECTS_DB
