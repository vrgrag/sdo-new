from pydantic import BaseModel, EmailStr
from typing import Literal

class UserBase(BaseModel):
    username: str
    email: EmailStr

class UserCreate(UserBase):
    password: str
    role: Literal["admin", "manager", "trainer", "student"] = "student"

class UserLogin(BaseModel):
    username: str
    password: str

class UserOut(BaseModel):
    id: int
    username: str
    email: EmailStr
    role: Literal["admin", "manager", "trainer", "student"]
