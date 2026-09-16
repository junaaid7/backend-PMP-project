from uuid import UUID

from pydantic import BaseModel, Field


class CreateTaskToolInput(BaseModel):
    title: str = Field(min_length=2, max_length=200)
    description: str | None = Field(default=None, max_length=1000)
    project_id: UUID
    status: str = "todo"


class UpdateTaskToolInput(BaseModel):
    task_id: UUID
    title: str | None = Field(default=None, min_length=2, max_length=200)
    description: str | None = Field(default=None, max_length=1000)
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


class AssistantRequest(BaseModel):
    command: str = Field(min_length=2, max_length=2000)
    project_id: UUID | None = None


class AssistantResponse(BaseModel):
    action: str
    message: str
    data: dict | list | None = None