from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field


class UserAnswerBase(BaseModel):
    user_id: int = Field(..., description="ID пользователя")
    question_id: int = Field(..., description="ID вопроса")
    selected_answer_id: Optional[int] = Field(None, description="ID выбранного ответа")
    is_correct: bool = Field(default=False, description="Правильно ли ответил")


class UserAnswerCreate(UserAnswerBase):
    pass


class UserAnswerUpdate(BaseModel):
    selected_answer_id: Optional[int] = None
    is_correct: Optional[bool] = None


class UserAnswerResponse(UserAnswerBase):
    id: int
    answered_at: datetime

    class Config:
        from_attributes = True

