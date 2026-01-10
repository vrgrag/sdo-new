from typing import List, Optional
from pydantic import BaseModel, Field


class QuestionBase(BaseModel):
    question_text: str = Field(..., description="Текст вопроса")
    question_type: str = Field(..., description="Тип вопроса (single_choice, multiple_choice, text)")
    test_id: int = Field(..., description="ID теста")


class QuestionCreate(QuestionBase):
    answers: List["AnswerCreate"] = Field(default_factory=list, description="Список вариантов ответов")


class QuestionUpdate(BaseModel):
    question_text: Optional[str] = None
    question_type: Optional[str] = None
    test_id: Optional[int] = None


class QuestionResponse(QuestionBase):
    id: int
    answers: List["AnswerResponse"] = []

    class Config:
        from_attributes = True


# Для forward references
from schemas.answer import AnswerCreate, AnswerResponse
QuestionCreate.model_rebuild()
QuestionResponse.model_rebuild()

