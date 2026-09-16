from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import (
    Project,
    Task,
    TaskStatus,
    User,
    UserRole,
)


WRITE_ROLES = {
    UserRole.OWNER,
    UserRole.ADMIN,
    UserRole.MANAGER,
    UserRole.DEVELOPER,
}


def _require_write_access(current_user: User):
    if current_user.role not in WRITE_ROLES:
        raise HTTPException(
            status_code=403,
            detail="You do not have permission to modify tasks",
        )


async def _get_project(
    project_id: UUID,
    current_user: User,
    db: AsyncSession,
):
    result = await db.execute(
        select(Project).where(
            Project.id == project_id,
            Project.organization_id == current_user.organization_id,
        )
    )

    project = result.scalar_one_or_none()

    if project is None:
        raise HTTPException(
            status_code=404,
            detail="Project not found",
        )

    return project


async def _get_user(
    user_id: UUID,
    current_user: User,
    db: AsyncSession,
):
    result = await db.execute(
        select(User).where(
            User.id == user_id,
            User.organization_id == current_user.organization_id,
        )
    )

    user = result.scalar_one_or_none()

    if user is None:
        raise HTTPException(
            status_code=404,
            detail="User not found in your organization",
        )

    return user


async def create_task_tool(
    data,
    current_user: User,
    db: AsyncSession,
):
    _require_write_access(current_user)

    project = await _get_project(
        data.project_id,
        current_user,
        db,
    )

    try:
        status = TaskStatus(data.status)
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail="Invalid task status",
        ) from exc

    task = Task(
        organization_id=current_user.organization_id,
        project_id=project.id,
        title=data.title.strip(),
        description=data.description.strip()
        if data.description
        else None,
        status=status,
    )

    db.add(task)

    await db.commit()
    await db.refresh(task)

    return task


async def update_task_tool(
    data,
    current_user: User,
    db: AsyncSession,
):
    _require_write_access(current_user)

    result = await db.execute(
        select(Task).where(
            Task.id == data.task_id,
            Task.organization_id == current_user.organization_id,
        )
    )

    task = result.scalar_one_or_none()

    if task is None:
        raise HTTPException(
            status_code=404,
            detail="Task not found",
        )

    if data.title is not None:
        task.title = data.title.strip()

    if data.description is not None:
        task.description = (
            data.description.strip() or None
        )

    if data.status is not None:
        try:
            task.status = TaskStatus(data.status)
        except ValueError as exc:
            raise HTTPException(
                status_code=400,
                detail="Invalid task status",
            ) from exc

    await db.commit()
    await db.refresh(task)

    return task


async def list_projects_tool(
    current_user: User,
    db: AsyncSession,
):
    result = await db.execute(
        select(Project).where(
            Project.organization_id
            == current_user.organization_id
        )
    )

    return result.scalars().all()


async def get_project_summary_tool(
    project_id: UUID,
    current_user: User,
    db: AsyncSession,
):
    project = await _get_project(
        project_id,
        current_user,
        db,
    )

    total_result = await db.execute(
        select(func.count(Task.id)).where(
            Task.project_id == project_id,
            Task.organization_id
            == current_user.organization_id,
        )
    )

    total_tasks = total_result.scalar() or 0

    todo_result = await db.execute(
        select(func.count(Task.id)).where(
            Task.project_id == project_id,
            Task.organization_id
            == current_user.organization_id,
            Task.status == TaskStatus.TODO,
        )
    )

    todo_tasks = todo_result.scalar() or 0

    progress_result = await db.execute(
        select(func.count(Task.id)).where(
            Task.project_id == project_id,
            Task.organization_id
            == current_user.organization_id,
            Task.status == TaskStatus.IN_PROGRESS,
        )
    )

    in_progress_tasks = progress_result.scalar() or 0

    done_result = await db.execute(
        select(func.count(Task.id)).where(
            Task.project_id == project_id,
            Task.organization_id
            == current_user.organization_id,
            Task.status == TaskStatus.DONE,
        )
    )

    completed_tasks = done_result.scalar() or 0

    return {
        "project_id": str(project.id),
        "project_name": project.name,
        "total_tasks": total_tasks,
        "todo_tasks": todo_tasks,
        "in_progress_tasks": in_progress_tasks,
        "completed_tasks": completed_tasks,
    }


async def assign_user_tool(
    task_id: UUID,
    user_id: UUID,
    current_user: User,
    db: AsyncSession,
):
    _require_write_access(current_user)

    task_result = await db.execute(
        select(Task).where(
            Task.id == task_id,
            Task.organization_id
            == current_user.organization_id,
        )
    )

    task = task_result.scalar_one_or_none()

    if task is None:
        raise HTTPException(
            status_code=404,
            detail="Task not found",
        )

    user = await _get_user(
        user_id,
        current_user,
        db,
    )

    task.assigned_user_id = user.id

    await db.commit()
    await db.refresh(task)

    return {
        "task_id": str(task.id),
        "assigned_user_id": str(user.id),
        "assigned_user_name": user.name,
    }


async def generate_project_report_tool(
    project_id: UUID | None,
    current_user: User,
    db: AsyncSession,
):
    project = None

    if project_id is not None:
        project = await _get_project(
            project_id,
            current_user,
            db,
        )

    filters = [
        Task.organization_id
        == current_user.organization_id
    ]

    if project is not None:
        filters.append(
            Task.project_id == project.id
        )

    result = await db.execute(
        select(Task).where(*filters)
    )

    tasks = result.scalars().all()

    counts = {
        status.value: 0
        for status in TaskStatus
    }

    for task in tasks:
        counts[task.status.value] += 1

    total = len(tasks)

    completion_rate = (
        round(
            (
                counts[TaskStatus.DONE.value]
                / total
            )
            * 100,
            1,
        )
        if total
        else 0
    )

    risks = []

    if total == 0:
        risks.append(
            "No tasks have been created yet"
        )

    if total and completion_rate < 25:
        risks.append(
            "Most work is still pending"
        )

    return {
        "project_id": (
            str(project.id)
            if project
            else None
        ),
        "project_name": (
            project.name
            if project
            else "Organization report"
        ),
        "total_tasks": total,
        "status_counts": counts,
        "completion_rate": completion_rate,
        "risks": risks,
    }