from fastapi import APIRouter, Depends

from app.dependencies import get_current_user, require_roles
from app.models import User, UserRole

router = APIRouter(
    prefix="/organizations",
    tags=["Organizations"],
)


@router.get("/me")
async def get_my_organization(
    current_user: User = Depends(get_current_user),
):
    return {
        "organization_id": current_user.organization_id,
        "role": current_user.role,
    }


@router.put("/me")
async def update_my_organization(
    current_user: User = Depends(
        require_roles(
            UserRole.OWNER,
            UserRole.ADMIN,
        )
    ),
):
    return {
        "message": "Only Owner or Admin can update organization",
        "organization_id": current_user.organization_id,
    }