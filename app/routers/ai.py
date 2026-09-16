from uuid import UUID
import re

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.schemas import (
    AssistantRequest,
    AssistantResponse,
    CreateTaskToolInput,
    UpdateTaskToolInput,
)
from app.ai.tools import (
    assign_user_tool,
    create_task_tool,
    generate_project_report_tool,
    get_project_summary_tool,
    list_projects_tool,
    update_task_tool,
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
    task = await create_task_tool(
        data=data,
        current_user=current_user,
        db=db,
    )

    return {
        "id": str(task.id),
        "project_id": str(task.project_id),
        "title": task.title,
        "description": task.description,
        "status": task.status.value,
    }


@router.patch("/tools/update-task")
async def update_task(
    data: UpdateTaskToolInput,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    task = await update_task_tool(
        data=data,
        current_user=current_user,
        db=db,
    )

    return {
        "id": str(task.id),
        "project_id": str(task.project_id),
        "title": task.title,
        "description": task.description,
        "status": task.status.value,
    }


@router.get("/tools/list-projects")
async def list_projects(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    projects = await list_projects_tool(
        current_user=current_user,
        db=db,
    )

    return [
        {
            "id": str(project.id),
            "name": project.name,
        }
        for project in projects
    ]


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


@router.post("/tools/assign-user")
async def assign_user(
    task_id: UUID,
    user_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await assign_user_tool(
        task_id=task_id,
        user_id=user_id,
        current_user=current_user,
        db=db,
    )


@router.get("/tools/project-report")
async def project_report(
    project_id: UUID | None = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await generate_project_report_tool(
        project_id=project_id,
        current_user=current_user,
        db=db,
    )


@router.post("/assistant", response_model=AssistantResponse)
async def assistant(
    data: AssistantRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    command = data.command.strip()
    normalized = command.lower()

    # LIST PROJECTS
    if normalized in {
        "list projects",
        "show projects",
        "my projects",
    }:
        projects = await list_projects_tool(
            current_user=current_user,
            db=db,
        )

        return AssistantResponse(
            action="list_projects",
            message=f"Found {len(projects)} project(s) in your organization.",
            data=[
                {
                    "id": str(project.id),
                    "name": project.name,
                }
                for project in projects
            ],
        )

    # CREATE TASK
    if any(
        keyword in normalized
        for keyword in (
            "create task",
            "add task",
            "new task",
        )
    ):
        if data.project_id is None:
            raise HTTPException(
                status_code=400,
                detail="Select a project before creating a task",
            )

        title = re.sub(
            r"^(please\s+)?(create|add|new)\s+task\s*:?-?\s*",
            "",
            command,
            flags=re.IGNORECASE,
        )

        title = re.split(
            r"\s+in\s+(?:the\s+)?project\s+",
            title,
            maxsplit=1,
            flags=re.IGNORECASE,
        )[0].strip()

        if len(title) < 2:
            raise HTTPException(
                status_code=400,
                detail="Add a task title to the command",
            )

        task = await create_task_tool(
            data=CreateTaskToolInput(
                title=title,
                project_id=data.project_id,
            ),
            current_user=current_user,
            db=db,
        )

        return AssistantResponse(
            action="create_task",
            message=f'Task "{task.title}" created successfully.',
            data={
                "id": str(task.id),
                "project_id": str(task.project_id),
                "title": task.title,
                "description": task.description,
                "status": task.status.value,
            },
        )

    # PROJECT SUMMARY
    if any(
        keyword in normalized
        for keyword in (
            "summary",
            "health",
            "status",
        )
    ):
        if data.project_id is None:
            raise HTTPException(
                status_code=400,
                detail="Select a project for a project summary",
            )

        summary = await get_project_summary_tool(
            project_id=data.project_id,
            current_user=current_user,
            db=db,
        )

        return AssistantResponse(
            action="project_summary",
            message=f"Summary generated for {summary['project_name']}.",
            data=summary,
        )

    # PROJECT REPORT
    if any(
        keyword in normalized
        for keyword in (
            "report",
            "risk",
            "workload",
        )
    ):
        report = await generate_project_report_tool(
            project_id=data.project_id,
            current_user=current_user,
            db=db,
        )

        report["risks"] = [
            risk
            for risk in report["risks"]
            if risk
        ]

        return AssistantResponse(
            action="generate_report",
            message=f"Report generated for {report['project_name']}.",
            data=report,
        )

    # COMMAND NOT FOUND
    raise HTTPException(
        status_code=422,
        detail=(
            "Try: list projects, create task, "
            "project summary, or generate report"
        ),
    )