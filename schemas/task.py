from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field


class TaskBase(BaseModel):
    title: str = Field(..., max_length=256, description="Название задания")
    description: Optional[str] = Field(None, max_length=256, description="Описание задания")
    status: Optional[str] = Field(None, description="Статус задания")
    deadline: Optional[datetime] = Field(None, description="Срок выполнения")
    assigned_to_user_id: Optional[int] = Field(None, description="ID назначенного пользователя")
    course_id: int = Field(..., description="ID курса")


class TaskCreate(TaskBase):
    pass


class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=256)
    description: Optional[str] = Field(None, max_length=256)
    status: Optional[str] = None
    deadline: Optional[datetime] = None
    assigned_to_user_id: Optional[int] = None
    course_id: Optional[int] = None


class TaskResponse(TaskBase):
    id: int
    date_created: Optional[datetime] = None
    created_at: Optional[datetime] = None
    created_by_id: Optional[int] = None

    class Config:
        from_attributes = True

