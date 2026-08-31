from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import User
from app.schemas import (
    UserCreate,
    UserUpdate,
    UserResponse,
)

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)


@router.post(
    "/",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED
)
async def create_user(
    user: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    new_user = User(
        name=user.name,
        email=user.email
    )

    db.add(new_user)

    try:
        await db.commit()
        await db.refresh(new_user)
    except Exception:
        await db.rollback()
        raise

    return new_user



@router.get(
    "/",
    response_model=list[UserResponse]
)
async def get_users(
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(User)
    )

    return result.scalars().all()


@router.get(
    "/{user_id}",
    response_model=UserResponse
)
async def get_user(
    user_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(User).where(User.id == user_id)
    )

    user = result.scalar_one_or_none()

    if user is None:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    return user


@router.put(
    "/{user_id}",
    response_model=UserResponse
)
async def update_user(
    user_id: UUID,
    user_data: UserUpdate,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(User).where(User.id == user_id)
    )

    user = result.scalar_one_or_none()

    if user is None:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    user.name = user_data.name
    user.email = user_data.email

    try:
        await db.commit()
        await db.refresh(user)
    except Exception:
        await db.rollback()
        raise

    return user


@router.delete("/{user_id}")
async def delete_user(
    user_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(User).where(User.id == user_id)
    )

    user = result.scalar_one_or_none()

    if user is None:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    try:
        await db.delete(user)
        await db.commit()
    except Exception:
        await db.rollback()
        raise

    return {
        "message": "User deleted successfully"
    }





