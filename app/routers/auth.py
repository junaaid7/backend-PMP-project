from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.dependencies import get_current_user
from app.schemas import UserResponse

from app.database import get_db
from app.models import User, Organization, UserRole
from app.schemas import UserRegister, UserLogin
from app.security import (
    hash_password,
    verify_password,
    create_access_token,
)


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
)
async def register(
    user_data: UserRegister,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(User).where(
            User.email == user_data.email
        )
    )

    existing_user = result.scalar_one_or_none()

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered",
        )

    organization_result = await db.execute(
        select(Organization).where(
            Organization.name == user_data.organization_name
        )
    )

    organization = organization_result.scalar_one_or_none()
    organization_created = False    

    if organization is None:
        organization = Organization(
            name=user_data.organization_name
        )

        db.add(organization)
        await db.flush()
        organization_created = True

    new_user = User(
        name=user_data.name,
        email=user_data.email,
        password_hash=hash_password(
            user_data.password
        ),
        organization_id=organization.id,
        role=(
        UserRole.OWNER
        if organization_created
        else UserRole.VIEWER
    )
    )

    db.add(new_user)
    await db.flush()

    if organization_created:
        organization.owner_id = new_user.id
    

    try:
        await db.commit()
        await db.refresh(new_user)

    except Exception:
        await db.rollback()
        raise

    return {
        "message": "User registered successfully"
    }


@router.post("/login")
async def login(
    user_data: UserLogin,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(User).where(
            User.email == user_data.email
        )
    )

    user = result.scalar_one_or_none()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    password_correct = verify_password(
        user_data.password,
        user.password_hash,
    )

    if not password_correct:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    access_token = create_access_token(
        str(user.id)
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
    }


# @router.get(
#     "/me",
#     response_model=UserResponse,
# )
# async def get_me(
#     current_user: User = Depends(get_current_user),
# ):
#     return current_user


@router.get("/me")
async def get_current_user(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Organization).where(
            Organization.id == current_user.organization_id
        )
    )

    organization = result.scalar_one_or_none()

    return {
        "id": current_user.id,
        "name": current_user.name,
        "email": current_user.email,
        "organization_id": current_user.organization_id,
        "organization_name": organization.name if organization else "Unknown Organization",
        "role": current_user.role.value,
    }