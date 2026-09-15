from fastapi import APIRouter, Depends
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user
from app.models import User, Project, Task, TaskStatus


router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"],
)




@router.get("/tasks")
async def get_dashboard_tasks(
    search: str | None = None,
    status: TaskStatus | None = None,
    project_id: str | None = None,
    page: int = 1,
    limit: int = 10,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    organization_id = current_user.organization_id

    if page < 1:
        page = 1

    if limit < 1:
        limit = 10

    if limit > 50:
        limit = 50

    query = select(Task).where(
        Task.organization_id == organization_id
    )

    # Search
    if search:
        query = query.where(
            Task.title.ilike(f"%{search}%")
        )

    # Status filter
    if status:
        query = query.where(
            Task.status == status
        )

    # Project filter
    if project_id:
        query = query.where(
            Task.project_id == project_id
        )

    # Count filtered tasks
    count_query = select(
        func.count(Task.id)
    ).where(
        Task.organization_id == organization_id
    )

    if search:
        count_query = count_query.where(
            Task.title.ilike(f"%{search}%")
        )

    if status:
        count_query = count_query.where(
            Task.status == status
        )

    if project_id:
        count_query = count_query.where(
            Task.project_id == project_id
        )

    count_result = await db.execute(count_query)

    total = count_result.scalar() or 0

    # Pagination
    offset = (page - 1) * limit

    query = query.offset(offset).limit(limit)

    result = await db.execute(query)

    tasks = result.scalars().all()

    return {
        "items": tasks,
        "page": page,
        "limit": limit,
        "total": total,
        "total_pages": (total + limit - 1) // limit,
    }


@router.get("/stats")
async def get_dashboard_stats(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    organization_id = current_user.organization_id

    # Total projects
    project_result = await db.execute(
        select(func.count(Project.id)).where(
            Project.organization_id == organization_id
        )
    )

    total_projects = project_result.scalar() or 0

    # Total tasks
    task_result = await db.execute(
        select(func.count(Task.id)).where(
            Task.organization_id == organization_id
        )
    )

    total_tasks = task_result.scalar() or 0

    # Todo
    todo_result = await db.execute(
        select(func.count(Task.id)).where(
            Task.organization_id == organization_id,
            Task.status == TaskStatus.TODO,
        )
    )

    todo_tasks = todo_result.scalar() or 0

    # In progress
    progress_result = await db.execute(
        select(func.count(Task.id)).where(
            Task.organization_id == organization_id,
            Task.status == TaskStatus.IN_PROGRESS,
        )
    )

    in_progress_tasks = progress_result.scalar() or 0

    # Completed
    completed_result = await db.execute(
        select(func.count(Task.id)).where(
            Task.organization_id == organization_id,
            Task.status == TaskStatus.DONE,
        )
    )

    completed_tasks = completed_result.scalar() or 0

    return {
        "total_projects": total_projects,
        "total_tasks": total_tasks,
        "todo_tasks": todo_tasks,
        "in_progress_tasks": in_progress_tasks,
        "completed_tasks": completed_tasks,
    }