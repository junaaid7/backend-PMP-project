from fastapi import APIRouter, Depends

from app.dependencies import get_current_user
from app.models import User

router = APIRouter(
    prefix="/organizations",
    tags=["Organizations"],
)


@router.get("/me")
async def get_my_organization(
    current_user: User = Depends(get_current_user),
):
    return {
        "organization_id": current_user.organization_id
    }