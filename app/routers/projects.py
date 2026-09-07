from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user, require_roles
from app.models import Project, User, UserRole
from app.schemas import (
    ProjectCreate,
    ProjectUpdate,
    ProjectResponse,
)


router = APIRouter(
    prefix="/projects",
    tags=["Projects"],
)


@router.post(
    "/",
    response_model=ProjectResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_project(
    project_data: ProjectCreate,
    current_user: User = Depends(
        require_roles(
        UserRole.OWNER,
        UserRole.ADMIN,
        UserRole.MANAGER,
        )
    ),
    db: AsyncSession = Depends(get_db),
):
    project = Project(
        name=project_data.name,
        description=project_data.description,
        organization_id=current_user.organization_id,
    )

    db.add(project)

    try:
        await db.commit()
        await db.refresh(project)
    except Exception:
        await db.rollback()
        raise

    return project


@router.get(
    "/",
    response_model=list[ProjectResponse],
)
async def get_projects(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Project).where(
            Project.organization_id
            == current_user.organization_id
        )
    )

    return result.scalars().all()


@router.get(
    "/{project_id}",
    response_model=ProjectResponse,
)
async def get_project(
    project_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Project).where(
            Project.id == project_id,
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

    return project


@router.put(
    "/{project_id}",
    response_model=ProjectResponse,
)
async def update_project(
    project_id: UUID,
    project_data: ProjectUpdate,
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
        select(Project).where(
            Project.id == project_id,
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

    project.name = project_data.name
    project.description = project_data.description

    try:
        await db.commit()
        await db.refresh(project)
    except Exception:
        await db.rollback()
        raise

    return project


@router.delete("/{project_id}")
async def delete_project(
    project_id: UUID,
        current_user: User = Depends(
        require_roles(
            UserRole.OWNER,
            UserRole.ADMIN,
        )
    ),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Project).where(
            Project.id == project_id,
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

    try:
        await db.delete(project)
        await db.commit()
    except Exception:
        await db.rollback()
        raise

    return {
        "message": "Project deleted successfully"
    }
