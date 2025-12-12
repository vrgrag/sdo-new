# api/v1/users.py
from typing import List, Optional

from fastapi import APIRouter, Query, HTTPException, Depends

from schemas.users import UserCreate, UserResponse, UserUpdate
from services.user_service import user_service
from core.security import get_current_user
from core.roles import UserRole

router = APIRouter(prefix="/users", tags=["Пользователи"])

@router.get("/", response_model=List[UserResponse])
def get_users(
    search: Optional[str] = Query(None, description="Поиск по ФИО, логину или email"),
    role: Optional[UserRole] = Query(None, description="Фильтр по роли"),
    company_id: Optional[int] = Query(None, description="Фильтр по компании"),
    department_id: Optional[int] = Query(None, description="Фильтр по отделу"),
    position_id: Optional[int] = Query(None, description="Фильтр по должности"),
    current_user: dict = Depends(get_current_user),
):
    users = user_service.get_visible_users(current_user)

    if search:
        s = search.lower()
        users = [
            u for u in users
            if s in (u.get("first_name") or "").lower()
            or s in (u.get("last_name") or "").lower()
            or s in (u.get("login") or "").lower()
            or s in (u.get("email") or "").lower()
        ]

    if role:
        users = [u for u in users if u.get("role") == role.value]

    if company_id is not None:
        users = [u for u in users if u.get("company_id") == company_id]
    if department_id is not None:
        users = [u for u in users if u.get("department_id") == department_id]
    if position_id is not None:
        users = [u for u in users if u.get("position_id") == position_id]

    return users

@router.post("/", response_model=UserResponse, status_code=201)
def create_user(
    user_in: UserCreate,
    current_user: dict = Depends(get_current_user),
):

    if current_user["role"] not in (UserRole.ADMIN.value, UserRole.MANAGER.value):
        raise HTTPException(status_code=403, detail="Недостаточно прав")

    created = user_service.create_user(user_in.dict())
    return created
@router.get("/me", response_model=UserResponse)
def get_me(current_user: dict = Depends(get_current_user)):
    return current_user

@router.get("/{user_id}", response_model=UserResponse)
def get_user(
    user_id: int,
    current_user: dict = Depends(get_current_user),
):
    user = user_service.get_by_id(user_id, current_user)
    return user
@router.patch("/{user_id}", response_model=UserResponse)
def update_user(
    user_id: int,
    update_data: UserUpdate,
    current_user: dict = Depends(get_current_user),
):
    updated = user_service.update_user(
        user_id,
        update_data.dict(exclude_unset=True),
        current_user=current_user,
    )
    return updated

@router.delete("/{user_id}")
def delete_user(
    user_id: int,
    current_user: dict = Depends(get_current_user),
):
    result = user_service.delete_user(user_id, current_user)
    return result
