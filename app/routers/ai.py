from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.schemas import CreateTaskToolInput
from app.ai.tools import (
    create_task_tool,
    list_projects_tool,
    get_project_summary_tool,
)
from app.database import get_db
from app.dependencies import get_current_user
from app.models import User


router = APIRouter(
    prefix="/ai",
    tags=["AI"],
)


@router.post("/tools/create-task")
async def create_task(
    data: CreateTaskToolInput,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await create_task_tool(
        data=data,
        current_user=current_user,
        db=db,
    )


@router.get("/tools/list-projects")
async def list_projects(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await list_projects_tool(
        current_user=current_user,
        db=db,
    )


@router.get("/tools/project-summary/{project_id}")
async def project_summary(
    project_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await get_project_summary_tool(
        project_id=project_id,
        current_user=current_user,
        db=db,
    )