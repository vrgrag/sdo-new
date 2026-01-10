# services/answer_service.py
from typing import List, Optional
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from schemas import AnswerResponse, AnswerCreate, AnswerUpdate
from repositories.mock.answer_repository import AnswerRepository
from repositories.mock.question_repository import QuestionRepository


class AnswerService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.answer_repo = AnswerRepository(db)
        self.question_repo = QuestionRepository(db)

    async def get_all_answers(
        self,
        question_id: Optional[int] = None
    ) -> List[AnswerResponse]:
        """Получить все ответы, опционально фильтровать по вопросу"""
        return await self.answer_repo.get_all(question_id)

    async def get_answer_by_id(self, answer_id: int) -> AnswerResponse:
        """Получить ответ по ID"""
        answer = await self.answer_repo.get_by_id(answer_id)
        if not answer:
            raise HTTPException(status_code=404, detail="Ответ не найден")
        return answer

    async def create_answer(self, answer_data: AnswerCreate) -> AnswerResponse:
        """Создать новый ответ"""
        # Проверяем что вопрос существует
        question = await self.question_repo.get_by_id(answer_data.question_id)
        if not question:
            raise HTTPException(status_code=404, detail="Вопрос не найден")
        
        return await self.answer_repo.create(answer_data)

    async def update_answer(self, answer_id: int, answer_data: AnswerUpdate) -> AnswerResponse:
        """Обновить ответ"""
        if answer_data.question_id:
            # Проверяем что вопрос существует
            question = await self.question_repo.get_by_id(answer_data.question_id)
            if not question:
                raise HTTPException(status_code=404, detail="Вопрос не найден")
        
        updated = await self.answer_repo.update(answer_id, answer_data)
        if not updated:
            raise HTTPException(status_code=404, detail="Ответ не найден")
        return updated

    async def delete_answer(self, answer_id: int) -> bool:
        """Удалить ответ"""
        success = await self.answer_repo.delete(answer_id)
        if not success:
            raise HTTPException(status_code=404, detail="Ответ не найден")
        return success

