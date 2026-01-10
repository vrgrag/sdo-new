from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field


class TestBase(BaseModel):
    title: str = Field(..., max_length=256, description="Название теста")
    description: Optional[str] = Field(None, max_length=256, description="Описание теста")
    number_of_attempts: Optional[int] = Field(None, description="Количество попыток")
    time_limit_minutes: Optional[int] = Field(None, description="Лимит времени в минутах")
    course_id: int = Field(..., description="ID курса")


class TestCreate(TestBase):
    pass


class TestUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=256)
    description: Optional[str] = Field(None, max_length=256)
    number_of_attempts: Optional[int] = None
    time_limit_minutes: Optional[int] = None
    course_id: Optional[int] = None


class TestResponse(TestBase):
    id: int
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class TestDetailResponse(TestResponse):
    questions: List["QuestionResponse"] = []


# Для forward references
from schemas.question import QuestionResponse
TestDetailResponse.model_rebuild()

