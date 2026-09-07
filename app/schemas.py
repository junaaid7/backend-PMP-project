from uuid import UUID

from pydantic import BaseModel, ConfigDict


class UserCreate(BaseModel):
    name: str
    email: str


class UserUpdate(BaseModel):
    name: str
    email: str



class UserRegister(BaseModel):
    name: str
    email: str
    password: str
    organization_name: str

class UserLogin(BaseModel):
    email: str
    password: str



class UserResponse(BaseModel):
    id: UUID
    name: str
    email: str
    organization_id: UUID
    role: str

    model_config = ConfigDict(from_attributes=True)


class ProjectCreate(BaseModel):
    name: str
    description: str | None = None


class ProjectUpdate(BaseModel):
    name: str
    description: str | None = None


class ProjectResponse(BaseModel):
    id: UUID
    organization_id: UUID
    name: str
    description: str | None

    model_config = ConfigDict(
        from_attributes=True
    )


class TaskCreate(BaseModel):
    title: str
    description: str | None = None
    project_id: UUID


class TaskUpdate(BaseModel):
    title: str
    description: str | None = None
    status: str


class TaskResponse(BaseModel):
    id: UUID
    organization_id: UUID
    project_id: UUID
    title: str
    description: str | None
    status: str

    model_config = ConfigDict(
        from_attributes=True
    )


class TaskStatusUpdate(BaseModel):
    status: str