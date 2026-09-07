from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user, require_roles
from app.models import Task, TaskStatus, Project, User, UserRole
from app.schemas import (
    TaskCreate,
    TaskUpdate,
    TaskResponse,
    TaskStatusUpdate
)

router = APIRouter(
    prefix="/tasks",
    tags=["Tasks"],
)


@router.post(
    "/",
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_task(
    task_data: TaskCreate,
    current_user: User = Depends(
        require_roles(
            UserRole.OWNER,
            UserRole.ADMIN,
            UserRole.MANAGER,
            UserRole.DEVELOPER,
        )
    ),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Project).where(
            Project.id == task_data.project_id,
            Project.organization_id
            == current_user.organization_id,
        )
    )

    project = result.scalar_one_or_none()

    if project is None:
        raise HTTPException(
            status_code=404,
            detail="Project not found",
        )

    task = Task(
        title=task_data.title,
        description=task_data.description,
        project_id=task_data.project_id,
        organization_id=current_user.organization_id,
    )

    db.add(task)

    try:
        await db.commit()
        await db.refresh(task)
    except Exception:
        await db.rollback()
        raise

    return task



@router.get(
    "/",
    response_model=list[TaskResponse],
)
async def get_tasks(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Task).where(
            Task.organization_id
            == current_user.organization_id
        )
    )

    return result.scalars().all()


@router.get(
    "/{task_id}",
    response_model=TaskResponse,
)
async def get_task(
    task_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Task).where(
            Task.id == task_id,
            Task.organization_id
            == current_user.organization_id,
        )
    )

    task = result.scalar_one_or_none()

    if task is None:
        raise HTTPException(
            status_code=404,
            detail="Task not found",
        )

    return task


@router.put(
    "/{task_id}",
    response_model=TaskResponse,
)
async def update_task(
    task_id: UUID,
    task_data: TaskUpdate,
        current_user: User = Depends(
        require_roles(
            UserRole.OWNER,
            UserRole.ADMIN,
            UserRole.MANAGER,
            UserRole.DEVELOPER,
        )
    ),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Task).where(
            Task.id == task_id,
            Task.organization_id
            == current_user.organization_id,
        )
    )

    task = result.scalar_one_or_none()

    if task is None:
        raise HTTPException(
            status_code=404,
            detail="Task not found",
        )

    task.title = task_data.title
    task.description = task_data.description
    task.status = TaskStatus(task_data.status)

    try:
        await db.commit()
        await db.refresh(task)
    except Exception:
        await db.rollback()
        raise

    return task


@router.delete("/{task_id}")
async def delete_task(
    task_id: UUID,
    current_user: User = Depends(
    require_roles(
        UserRole.OWNER,
        UserRole.ADMIN,
        UserRole.MANAGER,
    )
),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Task).where(
            Task.id == task_id,
            Task.organization_id
            == current_user.organization_id,
        )
    )

    task = result.scalar_one_or_none()

    if task is None:
        raise HTTPException(
            status_code=404,
            detail="Task not found",
        )

    try:
        await db.delete(task)
        await db.commit()
    except Exception:
        await db.rollback()
        raise

    return {
        "message": "Task deleted successfully"
    }



@router.patch(
    "/{task_id}/status",
    response_model=TaskResponse,
)
async def update_task_status( 
    task_id: UUID,
    task_data: TaskStatusUpdate,
    current_user: User = Depends(
    require_roles(
        UserRole.OWNER,
        UserRole.ADMIN,
        UserRole.MANAGER,
        UserRole.DEVELOPER,
    )
),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Task).where(
            Task.id == task_id,
            Task.organization_id
            == current_user.organization_id,
        )
    )

    task = result.scalar_one_or_none()

    if task is None:
        raise HTTPException(
            status_code=404,
            detail="Task not found",
        )

    try:
        task.status = TaskStatus(task_data.status)

    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Invalid task status",
        )

    try:
        await db.commit()
        await db.refresh(task)

    except Exception:
        await db.rollback()
        raise

    return task




@router.get(
    "/project/{project_id}",
    response_model=list[TaskResponse],
)
async def get_project_tasks(
    project_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Task).where(
            Task.project_id == project_id,
            Task.organization_id == current_user.organization_id,
        )
    )

    return result.scalars().all()