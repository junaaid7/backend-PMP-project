from uuid import UUID

from pydantic import BaseModel


class CreateTaskToolInput(BaseModel):
    title: str
    description: str | None = None
    project_id: UUID


class UpdateTaskToolInput(BaseModel):
    task_id: UUID
    title: str | None = None
    description: str | None = None
    status: str | None = None


class ListProjectsToolInput(BaseModel):
    pass


class ProjectSummaryToolInput(BaseModel):
    project_id: UUID


class AssignUserToolInput(BaseModel):
    task_id: UUID
    user_id: UUID


class GenerateReportToolInput(BaseModel):
    project_id: UUID | None = None