from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.database import get_db
from app.models import User
from app.schemas import UserCreate, UserResponse, UserUpdate


app = FastAPI()


@app.post("/users", response_model=UserResponse)
async def create_user(
    user: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    new_user = User(
        name=user.name,
        email=user.email
    )

    db.add(new_user)

    await db.commit()

    await db.refresh(new_user)

    return new_user
 

@app.get("/users", response_model=list[UserResponse])
async def get_users(
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(User)
    )

    users = result.scalars().all()

    return users



@app.put("/users/{user_id}", response_model=UserResponse)
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

    await db.commit()
    await db.refresh(user)

    return user


@app.delete("/users/{user_id}")
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

    await db.delete(user)
    await db.commit()

    return {
        "message": "User deleted successfully"
    }


