# services/question_service.py
from typing import List, Optional
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from schemas import QuestionResponse, QuestionCreate, QuestionUpdate
from repositories.mock.question_repository import QuestionRepository
from repositories.mock.test_repository import TestRepository


class QuestionService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.question_repo = QuestionRepository(db)
        self.test_repo = TestRepository(db)

    async def get_all_questions(
        self,
        test_id: Optional[int] = None
    ) -> List[QuestionResponse]:
        """Получить все вопросы, опционально фильтровать по тесту"""
        return await self.question_repo.get_all(test_id)

    async def get_question_by_id(self, question_id: int) -> QuestionResponse:
        """Получить вопрос по ID"""
        question = await self.question_repo.get_by_id(question_id)
        if not question:
            raise HTTPException(status_code=404, detail="Вопрос не найден")
        return question

    async def create_question(self, question_data: QuestionCreate) -> QuestionResponse:
        """Создать новый вопрос с ответами"""
        # Проверяем что тест существует
        test = await self.test_repo.get_by_id(question_data.test_id)
        if not test:
            raise HTTPException(status_code=404, detail="Тест не найден")
        
        return await self.question_repo.create(question_data)

    async def update_question(self, question_id: int, question_data: QuestionUpdate) -> QuestionResponse:
        """Обновить вопрос"""
        if question_data.test_id:
            # Проверяем что тест существует
            test = await self.test_repo.get_by_id(question_data.test_id)
            if not test:
                raise HTTPException(status_code=404, detail="Тест не найден")
        
        updated = await self.question_repo.update(question_id, question_data)
        if not updated:
            raise HTTPException(status_code=404, detail="Вопрос не найден")
        return updated

    async def delete_question(self, question_id: int) -> bool:
        """Удалить вопрос (ответы удалятся каскадно)"""
        success = await self.question_repo.delete(question_id)
        if not success:
            raise HTTPException(status_code=404, detail="Вопрос не найден")
        return success

