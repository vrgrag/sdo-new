from typing import List, Optional

from fastapi import APIRouter, Query, HTTPException, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from core.db import get_db
from schemas.users import UserCreate, UserResponse, UserUpdate
from services.user_service import user_service
from core.security import get_current_user
from core.roles import UserRole

router = APIRouter(prefix="/users", tags=["Пользователи"])

@router.get("/", response_model=List[UserResponse])
async def get_users(
    search: Optional[str] = Query(None, description="Поиск по ФИО, логину или email"),
    role_id: Optional[int] = Query(None, description="Фильтр по role_id"),
    company_id: Optional[int] = Query(None, description="Фильтр по компании"),
    department_id: Optional[int] = Query(None, description="Фильтр по отделу"),
    position_id: Optional[int] = Query(None, description="Фильтр по должности"),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    users = await user_service.get_visible_users(db, current_user)

    if search:
        s = search.lower()
        users = [
            u for u in users
            if s in (u.get("first_name") or "").lower()
            or s in (u.get("last_name") or "").lower()
            or s in (u.get("login") or "").lower()
            or s in (u.get("email") or "").lower()
        ]

    if role_id is not None:
        users = [u for u in users if u.get("role_id") == role_id]

    if company_id is not None:
        users = [u for u in users if u.get("company_id") == company_id]
    if department_id is not None:
        users = [u for u in users if u.get("department_id") == department_id]
    if position_id is not None:
        users = [u for u in users if u.get("position_id") == position_id]

    return users


@router.post("/", response_model=UserResponse, status_code=201)
async def create_user(
    request: Request,
    user_in: UserCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    return await user_service.create_user(db, user_in.model_dump(), current_user)


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: dict = Depends(get_current_user)):
    return current_user


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    return await user_service.get_by_id(db, user_id, current_user)


@router.patch("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    update_data: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    return await user_service.update_user(
        db,
        user_id,
        update_data.model_dump(exclude_unset=True),
        current_user=current_user,
    )


@router.delete("/{user_id}")
async def delete_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    return await user_service.delete_user(db, user_id, current_user)
