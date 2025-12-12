"""
models.py - Pydantic модели для запросов и ответов
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

# Импортируем Enum из database.py
from database import CourseStatus, ContentType, LessonType, UserRole


class UserBase(BaseModel):
    email: str
    full_name: str
    role: UserRole = UserRole.STUDENT
    avatar_url: Optional[str] = None


class UserCreate(UserBase):
    password: str


class UserResponse(UserBase):
    id: int
    created_at: datetime
    is_active: bool

    class Config:
        orm_mode = True
        from_attributes = True


class CourseBase(BaseModel):
    title: str
    description: str
    short_description: Optional[str] = None
    code: str
    status: CourseStatus = CourseStatus.DRAFT
    image_url: Optional[str] = None
    duration_hours: int = 0
    tags: List[str] = Field(default_factory=list)
    requirements: List[str] = Field(default_factory=list)
    what_you_learn: List[str] = Field(default_factory=list)


class CourseCreate(CourseBase):
    created_by_id: int
    assigned_manager_id: Optional[int] = None


class CourseResponse(CourseBase):
    id: int
    created_by_id: int
    assigned_manager_id: Optional[int]
    created_at: datetime
    updated_at: datetime
    default_image_url: str = "/static/default_course_image.jpg"

    class Config:
        orm_mode = True
        from_attributes = True


class CourseModuleBase(BaseModel):
    title: str
    description: Optional[str] = None
    order: int = 0
    is_published: bool = True


class CourseModuleCreate(CourseModuleBase):
    course_id: int


class CourseModuleResponse(CourseModuleBase):
    id: int
    course_id: int
    created_at: datetime

    class Config:
        orm_mode = True
        from_attributes = True


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
    module_id: int


class LessonResponse(LessonBase):
    id: int
    module_id: int
    created_at: datetime

    class Config:
        orm_mode = True
        from_attributes = True


class EnrollmentBase(BaseModel):
    user_id: int
    course_id: int


class EnrollmentResponse(BaseModel):
    id: int
    user_id: int
    course_id: int
    enrolled_at: datetime
    progress_percentage: float = 0.0
    current_lesson_id: Optional[int] = None
    completed_at: Optional[datetime] = None
    last_accessed: datetime
    is_active: bool = True

    class Config:
        orm_mode = True
        from_attributes = True


class LessonProgressBase(BaseModel):
    enrollment_id: int
    lesson_id: int
    is_completed: bool = False
    time_spent_minutes: int = 0


class LessonProgressResponse(LessonProgressBase):
    id: int
    completed_at: Optional[datetime] = None
    last_accessed: datetime

    class Config:
        orm_mode = True
        from_attributes = True


class TestBase(BaseModel):
    title: str
    description: Optional[str] = None
    questions: List[Dict[str, Any]] = []
    passing_score: int = 70
    time_limit_minutes: Optional[int] = None
    max_attempts: int = 3
    is_published: bool = True


class TestCreate(TestBase):
    module_id: int


class TestResponse(TestBase):
    id: int
    module_id: int
    created_at: datetime

    class Config:
        orm_mode = True
        from_attributes = True


class CourseCard(BaseModel):
    """Упрощенная модель для отображения курса в списке"""
    id: int
    title: str
    short_description: Optional[str]
    code: str
    image_url: Optional[str]
    status: CourseStatus

    created_by_name: str
    manager_name: Optional[str]


class CourseDetails(CourseResponse):
    """Полная информация о курсе"""
    creator_info: Dict[str, Any]
    manager_info: Optional[Dict[str, Any]]
    stats: Dict[str, Any]
    modules: List[Dict[str, Any]]
    is_enrolled: bool = False