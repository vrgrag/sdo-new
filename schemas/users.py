# schemas/users.py
from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import List, Optional
from datetime import date



class UserBase(BaseModel):
    login: str = Field(..., example="ivanov")
    email: EmailStr = Field(..., example="ivanov@company.com")
    first_name: str = Field(..., example="Иван")
    last_name: str = Field(..., example="Иванов")
    role: str  = Field(..., example="admin")



class UserCreate(UserBase):
    password: str = Field(..., min_length=6, example="password123")
    password_confirm: str = Field(..., min_length=6)

    company_id: Optional[int] = None
    department_id: Optional[int] = None
    position_id: Optional[int] = None

    birth_date: Optional[date] = None
    development_plan_id: Optional[int] = None
    group_ids: List[int] = Field(default_factory=list)
    program_ids: List[int] = Field(default_factory=list)

    @field_validator("password_confirm")
    @classmethod
    def passwords_match(cls, v, info):
        pw = info.data.get("password")
        if pw is not None and v != pw:
            raise ValueError("Пароли не совпадают")
        return v


class UserUpdate(BaseModel):
    login: Optional[str] = None
    email: Optional[EmailStr] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None

    role: Optional[str] = None

    company_id: Optional[int] = None
    department_id: Optional[int] = None
    position_id: Optional[int] = None
    birth_date: Optional[date] = None
    development_plan_id: Optional[int] = None
    group_ids: Optional[List[int]] = None
    program_ids: Optional[List[int]] = None

    password: Optional[str] = Field(None, min_length=6)
    password_confirm: Optional[str] = Field(None, min_length=6)

    @field_validator("password_confirm")
    @classmethod
    def passwords_match(cls, v, info):
        pw = info.data.get("password")
        if pw is not None and v != pw:
            raise ValueError("Пароли не совпадают")
        return v


class UserResponse(BaseModel):
    id: int
    login: str
    email: str
    first_name: str
    last_name: str
    role: Optional[str] = None
    role_id: Optional[int] = None

    company_id: Optional[int] = None
    department_id: Optional[int] = None
    position_id: Optional[int] = None
    birth_date: Optional[str] = None
    development_plan_id: Optional[int] = None
    group_ids: List[int] = Field(default_factory=list)
    program_ids: List[int] = Field(default_factory=list)
    last_login_at: Optional[str] = None
    rating: Optional[int] = 0

    class Config:
        from_attributes = True