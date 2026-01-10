from typing import Optional
from pydantic import BaseModel, Field


class AnswerBase(BaseModel):
    answer_text: str = Field(..., description="Текст ответа")
    is_correct: bool = Field(default=False, description="Правильный ли это ответ")
    question_id: int = Field(..., description="ID вопроса")


class AnswerCreate(AnswerBase):
    pass


class AnswerUpdate(BaseModel):
    answer_text: Optional[str] = None
    is_correct: Optional[bool] = None
    question_id: Optional[int] = None


class AnswerResponse(AnswerBase):
    id: int

    class Config:
        from_attributes = True

