from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from core.db import get_db
from repositories.mock.user_repository import UserRepository
from core.security import verify_password, create_access_token

router = APIRouter(prefix="/auth", tags=["Auth"])


class LoginRequest(BaseModel):
    login: str
    password: str


class LoginUserInfo(BaseModel):
    id: int
    login: str
    role: str | None = None
    role_id: int | None = None
    first_name: str | None = None
    last_name: str | None = None
    email: str | None = None


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: LoginUserInfo


@router.post("/login", response_model=LoginResponse)
async def login(data: LoginRequest, db: Session = Depends(get_db)):
    repo = UserRepository(db)

    # login на фронте == email в БД
    user = repo.get_by_login(data.login)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неправильный логин или пароль",
            headers={"WWW-Authenticate": "Bearer"},
        )

    password_hash = user.get("password_hash") or user.get("hashed_password")
    if not password_hash or not verify_password(data.password, password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неправильный логин или пароль",
            headers={"WWW-Authenticate": "Bearer"},
        )

    repo.update_last_login(user["id"])

    access_token = create_access_token(
        {
            "sub": user.get("email") or data.login,
            "role": user.get("role") or user.get("role_id"),
            "user_id": user["id"],
        }
    )

    user_public = LoginUserInfo(
        id=user["id"],
        login=user.get("email") or data.login,
        role=user.get("role"),
        role_id=user.get("role_id"),
        first_name=user.get("first_name"),
        last_name=user.get("last_name"),
        email=user.get("email"),
    )

    return LoginResponse(
        access_token=access_token,
        user=user_public,
    )
