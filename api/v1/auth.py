# api/v1/auth.py
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from repositories.mock.user_repository import user_repository
from core.security import verify_password, create_access_token

router = APIRouter(prefix="/auth", tags=["Auth"])


class LoginRequest(BaseModel):
    login: str
    password: str


class LoginUserInfo(BaseModel):
    id: int
    login: str
    role: str
    first_name: str | None = None
    last_name: str | None = None
    email: str | None = None


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: LoginUserInfo


@router.post("/login", response_model=LoginResponse)
async def login(data: LoginRequest):
    user = user_repository.get_by_login(data.login)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неправильный логин или пароль",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not verify_password(data.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неправильный логин или пароль",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user_repository.update_last_login(user["id"])

    access_token = create_access_token(
        {
            "sub": user["login"],
            "role": user["role"],
            "user_id": user["id"],
        }
    )
    user_public = LoginUserInfo(
        id=user["id"],
        login=user["login"],
        role=user["role"],
        first_name=user.get("first_name"),
        last_name=user.get("last_name"),
        email=user.get("email"),
    )

    return LoginResponse(
        access_token=access_token,
        user=user_public,
    )
