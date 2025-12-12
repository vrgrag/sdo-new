from typing import Optional
from pydantic import BaseModel
from .common import ContentType, LessonType


class LessonBase(BaseModel):
    title: str
    content_type: ContentType
    content_url: Optional[str] = None
    content_text: Optional[str] = None
    duration_minutes: int = 0
    order: int = 0
    lesson_type: LessonType = LessonType.THEORY
    is_published: bool = True


class LessonCreate(LessonBase):
    module_id: int  # нужно при создании


class LessonUpdate(BaseModel):
    title: Optional[str] = None
    content_type: Optional[ContentType] = None
    content_url: Optional[str] = None
    content_text: Optional[str] = None
    duration_minutes: Optional[int] = None
    order: Optional[int] = None
    lesson_type: Optional[LessonType] = None
    is_published: Optional[bool] = None


class LessonResponse(LessonBase):
    id: int

    class Config:
        from_attributes = True  # ← для SQLAlchemy (раньше было orm_mode)mo