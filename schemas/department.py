# schemas/department.py
from pydantic import BaseModel, Field
from typing import Optional


class DepartmentBase(BaseModel):
    name: str = Field(..., example="IT отдел", description="Название отдела")
    company_id: int = Field(..., description="ID компании (обязательно)")


class DepartmentCreate(DepartmentBase):
    pass


class DepartmentUpdate(BaseModel):
    name: Optional[str] = Field(None, example="Новый отдел")
    company_id: Optional[int] = Field(None, description="ID компании")


class DepartmentResponse(DepartmentBase):
    id: int
    company_id: int

    class Config:
        from_attributes = True

