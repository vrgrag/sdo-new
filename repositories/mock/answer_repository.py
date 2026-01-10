from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from schemas import AnswerResponse, AnswerCreate, AnswerUpdate
from models.answers import Answer


class AnswerRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    def _to_response(self, answer: Answer) -> AnswerResponse:
        """Преобразует модель Answer в AnswerResponse"""
        return AnswerResponse(
            id=answer.id,
            answer_text=answer.answer_text,
            is_correct=answer.is_correct,
            question_id=answer.question_id,
        )

    async def get_all(
        self,
        question_id: Optional[int] = None
    ) -> List[AnswerResponse]:
        """Получить все ответы, опционально фильтровать по вопросу"""
        stmt = select(Answer)
        
        if question_id is not None:
            stmt = stmt.where(Answer.question_id == question_id)
        
        res = await self.db.execute(stmt)
        answers = res.scalars().all()
        return [self._to_response(a) for a in answers]

    async def get_by_id(self, answer_id: int) -> Optional[AnswerResponse]:
        """Получить ответ по ID"""
        answer = await self.db.get(Answer, answer_id)
        if not answer:
            return None
        return self._to_response(answer)

    async def create(self, answer: AnswerCreate) -> AnswerResponse:
        """Создать новый ответ"""
        answer_obj = Answer(
            answer_text=answer.answer_text,
            is_correct=answer.is_correct,
            question_id=answer.question_id,
        )
        self.db.add(answer_obj)
        try:
            await self.db.commit()
        except IntegrityError:
            await self.db.rollback()
            raise
        await self.db.refresh(answer_obj)
        return self._to_response(answer_obj)

    async def update(self, answer_id: int, answer_data: AnswerUpdate) -> Optional[AnswerResponse]:
        """Обновить ответ"""
        answer = await self.db.get(Answer, answer_id)
        if not answer:
            return None
        
        update_data = answer_data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            if value is not None:
                setattr(answer, key, value)
        
        try:
            await self.db.commit()
        except IntegrityError:
            await self.db.rollback()
            raise
        
        await self.db.refresh(answer)
        return self._to_response(answer)

    async def delete(self, answer_id: int) -> bool:
        """Удалить ответ"""
        answer = await self.db.get(Answer, answer_id)
        if not answer:
            return False
        await self.db.delete(answer)
        await self.db.commit()
        return True

