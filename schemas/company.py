# schemas/company.py
from pydantic import BaseModel, Field
from typing import Optional


class CompanyBase(BaseModel):
    name: str = Field(..., example="ООО Компания", description="Название компании")


class CompanyCreate(CompanyBase):
    pass


class CompanyUpdate(BaseModel):
    name: Optional[str] = Field(None, example="ООО Новая Компания")


class CompanyResponse(CompanyBase):
    id: int

    class Config:
        from_attributes = True

