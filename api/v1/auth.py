from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from core.db import get_db
from repositories.mock.user_repository import UserRepository
from repositories.mock.role_repository import RoleRepository

from core.security import verify_password, create_access_token

router = APIRouter(prefix="/auth", tags=["Auth"])


class LoginRequest(BaseModel):
    login: str
    password: str


class LoginUserInfo(BaseModel):
    id: int
    login: str
    role_id: int | None = None
    role: str | None = None
    first_name: str
    last_name: str
    email: str
    first_name: str | None = None
    last_name: str | None = None
    email: str | None = None


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: LoginUserInfo


@router.post("/login", response_model=LoginResponse)
async def login(data: LoginRequest, db: AsyncSession = Depends(get_db)):
    repo = UserRepository(db)

    user = await repo.get_auth_user(data.login)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Неправильный логин или пароль")

    if not verify_password(data.password, user["password_hash"]):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Неправильный логин или пароль")

    await repo.update_last_login(user["id"])

    role_title = None
    if user.get("role_id") is not None:
        role_repo = RoleRepository(db)
        role_title = await role_repo.get_title_by_id(user["role_id"])

    access_token = create_access_token(
        {
            "sub": str(user["id"]),
            "user_id": user["id"],
            "role_id": user.get("role_id"),
            "role": role_title,
        }
    )

    return LoginResponse(
        access_token=access_token,
        user=LoginUserInfo(
            id=user["id"],
            login=user.get("login") or user.get("email"),
            role_id=user.get("role_id"),
            role=role_title,
            first_name=user.get("first_name"),
            last_name=user.get("last_name"),
            email=user.get("email"),
        ),
    )
