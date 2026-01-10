from typing import Optional
from pydantic import BaseModel, Field


class MaterialBase(BaseModel):
    title: str = Field(..., max_length=256, description="Название материала")
    number_of_pages: Optional[int] = Field(None, description="Количество страниц")
    description: str = Field(..., description="Описание материала")
    file_path: str = Field(..., max_length=256, description="Путь к файлу")
    course_id: int = Field(..., description="ID курса")


class MaterialCreate(MaterialBase):
    pass


class MaterialUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=256)
    number_of_pages: Optional[int] = None
    description: Optional[str] = None
    file_path: Optional[str] = Field(None, max_length=256)
    course_id: Optional[int] = None


class MaterialResponse(MaterialBase):
    id: int

    class Config:
        from_attributes = True

