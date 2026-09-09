from fastapi import APIRouter, Depends, HTTPException, status

from app.dependencies import get_current_user, require_roles
from app.models import User, UserRole, Organization
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from app.database import get_db
from app.schemas import MemberResponse, MemberRoleUpdate

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



@router.get(
    "/members",
    response_model=list[MemberResponse],
)
async def get_team_members(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    organization_result = await db.execute(
        select(Organization).where(
            Organization.id == current_user.organization_id
        )
    )

    organization = organization_result.scalar_one_or_none()

    if organization is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found",
        )

    members_result = await db.execute(
        select(User).where(
            User.organization_id == current_user.organization_id
        )
    )

    members = members_result.scalars().all()

    return [
        MemberResponse(
            id=member.id,
            name=member.name,
            email=member.email,
            organization_id=member.organization_id,
            role=member.role,
            is_organization_owner=(
                member.id == organization.owner_id
            ),
        )
        for member in members
    ]



@router.patch(
    "/members/{user_id}/role",
    response_model=MemberResponse,
)
async def update_member_role(
    user_id: UUID,
    role_data: MemberRoleUpdate,
    current_user: User = Depends(
        require_roles(
            UserRole.OWNER,
            UserRole.ADMIN,
        )
    ),
    db: AsyncSession = Depends(get_db),
):
    organization_result = await db.execute(
        select(Organization).where(
            Organization.id == current_user.organization_id
        )
    )

    organization = organization_result.scalar_one_or_none()

    if organization is None:
        raise HTTPException(
            status_code=404,
            detail="Organization not found",
        )

    member_result = await db.execute(
        select(User).where(
            User.id == user_id,
            User.organization_id == current_user.organization_id,
        )
    )

    member = member_result.scalar_one_or_none()

    if member is None:
        raise HTTPException(
            status_code=404,
            detail="Member not found",
        )

    # Nobody can change their own role
    if member.id == current_user.id:
        raise HTTPException(
            status_code=400,
            detail="You cannot change your own role",
        )

    current_user_is_real_owner = (
        current_user.id == organization.owner_id
    )

    target_is_real_owner = (
        member.id == organization.owner_id
    )

    # Only the real owner can change the real owner's role
    if target_is_real_owner and not current_user_is_real_owner:
        raise HTTPException(
            status_code=403,
            detail="Only the organization owner can change the owner's role",
        )

    # Only the real owner can assign the Owner role
    if (
        role_data.role == UserRole.OWNER
        and not current_user_is_real_owner
    ):
        raise HTTPException(
            status_code=403,
            detail="Only the organization owner can assign the Owner role",
        )

    member.role = role_data.role

    await db.commit()
    await db.refresh(member)

    return MemberResponse(
        id=member.id,
        name=member.name,
        email=member.email,
        organization_id=member.organization_id,
        role=member.role,
        is_organization_owner=(
            member.id == organization.owner_id
        ),
    )


@router.delete("/members/{user_id}")
async def remove_team_member(
    user_id: UUID,
    current_user: User = Depends(
        require_roles(
            UserRole.OWNER,
            UserRole.ADMIN,
        )
    ),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(User).where(
            User.id == user_id,
            User.organization_id == current_user.organization_id,
        )
    )

    member = result.scalar_one_or_none()

    if member is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Member not found",
        )

    if member.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot remove yourself",
        )

    await db.delete(member)
    await db.commit()

    return {
        "message": "Member removed successfully"
    }







