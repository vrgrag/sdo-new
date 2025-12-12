from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from .common import CourseStatus
from .module import ModuleResponse  # ← вложенность: курс → модули


class CourseBase(BaseModel):
    title: str
    description: str
    short_description: Optional[str] = None
    image_url: Optional[str] = None
    duration_hours: int = 0
    tags: List[str] = []
    requirements: List[str] = []
    what_you_learn: List[str] = []


class CourseCreate(CourseBase):
    pass


class CourseUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    short_description: Optional[str] = None
    image_url: Optional[str] = None
    duration_hours: Optional[int] = None
    tags: Optional[List[str]] = None
    requirements: Optional[List[str]] = None
    what_you_learn: Optional[List[str]] = None


class CourseResponse(CourseBase):
    id: int
    status: CourseStatus

    class Config:
        from_attributes = True


class CourseDetailResponse(CourseResponse):
    modules: List[ModuleResponse] = []
    enrollment_info: Optional[Dict[str, Any]] = None