from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import (
    User,
    Project,
    Task,
    TaskStatus,
)


async def create_task_tool(
    data,
    current_user: User,
    db: AsyncSession,
):
    project_result = await db.execute(
        select(Project).where(
            Project.id == data.project_id,
            Project.organization_id == current_user.organization_id,
        )
    )

    project = project_result.scalar_one_or_none()

    if project is None:
        raise HTTPException(
            status_code=404,
            detail="Project not found",
        )

    task = Task(
        organization_id=current_user.organization_id,
        project_id=project.id,
        title=data.title,
        description=data.description,
        status=TaskStatus.TODO,
    )

    db.add(task)

    await db.commit()
    await db.refresh(task)

    return task


async def list_projects_tool(
    current_user: User,
    db: AsyncSession,
):
    result = await db.execute(
        select(Project).where(
            Project.organization_id == current_user.organization_id
        )
    )

    projects = result.scalars().all()

    return projects


async def get_project_summary_tool(
    project_id: UUID,
    current_user: User,
    db: AsyncSession,
):
    project_result = await db.execute(
        select(Project).where(
            Project.id == project_id,
            Project.organization_id == current_user.organization_id,
        )
    )

    project = project_result.scalar_one_or_none()

    if project is None:
        raise HTTPException(
            status_code=404,
            detail="Project not found",
        )

    total_result = await db.execute(
        select(func.count(Task.id)).where(
            Task.project_id == project_id,
            Task.organization_id == current_user.organization_id,
        )
    )

    total_tasks = total_result.scalar() or 0

    todo_result = await db.execute(
        select(func.count(Task.id)).where(
            Task.project_id == project_id,
            Task.organization_id == current_user.organization_id,
            Task.status == TaskStatus.TODO,
        )
    )

    todo_tasks = todo_result.scalar() or 0

    progress_result = await db.execute(
        select(func.count(Task.id)).where(
            Task.project_id == project_id,
            Task.organization_id == current_user.organization_id,
            Task.status == TaskStatus.IN_PROGRESS,
        )
    )

    in_progress_tasks = progress_result.scalar() or 0

    done_result = await db.execute(
        select(func.count(Task.id)).where(
            Task.project_id == project_id,
            Task.organization_id == current_user.organization_id,
            Task.status == TaskStatus.DONE,
        )
    )

    completed_tasks = done_result.scalar() or 0

    return {
        "project_id": project.id,
        "project_name": project.name,
        "total_tasks": total_tasks,
        "todo_tasks": todo_tasks,
        "in_progress_tasks": in_progress_tasks,
        "completed_tasks": completed_tasks,
    }