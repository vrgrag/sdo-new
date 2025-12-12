# 📁 schemas/module.py
from typing import List, Optional
from pydantic import BaseModel
from .lesson import LessonResponse


class ModuleBase(BaseModel):
    title: str
    description: Optional[str] = None
    order: int = 0
    is_published: bool = True


class ModuleCreate(ModuleBase):
    course_id: int


class ModuleUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    order: Optional[int] = None
    is_published: Optional[bool] = None


class ModuleResponse(ModuleBase):
    id: int
    lessons: List[LessonResponse] = []

    class Config:
        from_attributes = True