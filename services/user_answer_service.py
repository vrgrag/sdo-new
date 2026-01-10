# services/user_answer_service.py
from typing import List, Optional
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from schemas import UserAnswerResponse, UserAnswerCreate, UserAnswerUpdate
from repositories.mock.user_answer_repository import UserAnswerRepository
from repositories.mock.question_repository import QuestionRepository
from repositories.mock.answer_repository import AnswerRepository


class UserAnswerService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.user_answer_repo = UserAnswerRepository(db)
        self.question_repo = QuestionRepository(db)
        self.answer_repo = AnswerRepository(db)

    async def get_all_user_answers(
        self,
        user_id: Optional[int] = None,
        question_id: Optional[int] = None,
        test_id: Optional[int] = None
    ) -> List[UserAnswerResponse]:
        """Получить все ответы пользователей"""
        return await self.user_answer_repo.get_all(user_id, question_id, test_id)

    async def get_user_answer_by_id(self, user_answer_id: int) -> UserAnswerResponse:
        """Получить ответ пользователя по ID"""
        user_answer = await self.user_answer_repo.get_by_id(user_answer_id)
        if not user_answer:
            raise HTTPException(status_code=404, detail="Ответ пользователя не найден")
        return user_answer

    async def create_user_answer(self, user_answer_data: UserAnswerCreate) -> UserAnswerResponse:
        """Создать ответ пользователя на вопрос"""
        # Проверяем что вопрос существует
        question = await self.question_repo.get_by_id(user_answer_data.question_id)
        if not question:
            raise HTTPException(status_code=404, detail="Вопрос не найден")
        
        # Проверяем что выбранный ответ существует (если указан)
        if user_answer_data.selected_answer_id:
            answer = await self.answer_repo.get_by_id(user_answer_data.selected_answer_id)
            if not answer:
                raise HTTPException(status_code=404, detail="Ответ не найден")
            
            # Проверяем что ответ принадлежит этому вопросу
            if answer.question_id != user_answer_data.question_id:
                raise HTTPException(status_code=400, detail="Ответ не принадлежит этому вопросу")
            
            # Автоматически определяем правильность ответа
            if user_answer_data.is_correct is None:
                user_answer_data.is_correct = answer.is_correct
        
        return await self.user_answer_repo.create(user_answer_data)

    async def update_user_answer(self, user_answer_id: int, user_answer_data: UserAnswerUpdate) -> UserAnswerResponse:
        """Обновить ответ пользователя"""
        if user_answer_data.selected_answer_id:
            # Проверяем что ответ существует
            answer = await self.answer_repo.get_by_id(user_answer_data.selected_answer_id)
            if not answer:
                raise HTTPException(status_code=404, detail="Ответ не найден")
            
            # Обновляем правильность ответа автоматически
            if user_answer_data.is_correct is None:
                user_answer_data.is_correct = answer.is_correct
        
        updated = await self.user_answer_repo.update(user_answer_id, user_answer_data)
        if not updated:
            raise HTTPException(status_code=404, detail="Ответ пользователя не найден")
        return updated

    async def delete_user_answer(self, user_answer_id: int) -> bool:
        """Удалить ответ пользователя"""
        success = await self.user_answer_repo.delete(user_answer_id)
        if not success:
            raise HTTPException(status_code=404, detail="Ответ пользователя не найден")
        return success

