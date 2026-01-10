from typing import List, Literal, Optional, Union
from pydantic import BaseModel, Field


class ModuleItemBase(BaseModel):
    type: Literal["lesson", "test", "assignment"]
    id: int
    title: str
    order: int = 0
    is_published: bool = True

class LessonItem(ModuleItemBase):
    type: Literal["lesson"] = "lesson"
    duration_minutes: int = 0
    content_type: str
    content_text: Optional[str] = None
    content_url: Optional[str] = None
    lesson_type: str


class CourseContentResponse(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    status: Optional[str] = None

    lessons: List[LessonItem] = Field(default_factory=list)
