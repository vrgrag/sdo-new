from typing import List, Optional
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from datetime import datetime

from schemas import UserAnswerResponse, UserAnswerCreate, UserAnswerUpdate
from models.users_answers import UserAnswer


class UserAnswerRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    def _to_response(self, user_answer: UserAnswer) -> UserAnswerResponse:
        """Преобразует модель UserAnswer в UserAnswerResponse"""
        return UserAnswerResponse(
            id=user_answer.id,
            user_id=user_answer.user_id,
            question_id=user_answer.question_id,
            selected_answer_id=user_answer.selected_answer_id,
            is_correct=user_answer.is_correct,
            answered_at=user_answer.answered_at,
        )

    async def get_all(
        self,
        user_id: Optional[int] = None,
        question_id: Optional[int] = None,
        test_id: Optional[int] = None
    ) -> List[UserAnswerResponse]:
        """Получить все ответы пользователей, опционально фильтровать"""
        from models.questions import Question
        
        if test_id is not None:
            # Нужно джойнить через questions
            stmt = select(UserAnswer).join(Question, Question.id == UserAnswer.question_id)
        else:
            stmt = select(UserAnswer)
        
        conditions = []
        if user_id is not None:
            conditions.append(UserAnswer.user_id == user_id)
        if question_id is not None:
            conditions.append(UserAnswer.question_id == question_id)
        if test_id is not None:
            conditions.append(Question.test_id == test_id)
        
        if conditions:
            stmt = stmt.where(and_(*conditions))
        
        res = await self.db.execute(stmt)
        user_answers = res.scalars().all()
        return [self._to_response(ua) for ua in user_answers]

    async def get_by_id(self, user_answer_id: int) -> Optional[UserAnswerResponse]:
        """Получить ответ пользователя по ID"""
        user_answer = await self.db.get(UserAnswer, user_answer_id)
        if not user_answer:
            return None
        return self._to_response(user_answer)

    async def get_by_user_and_question(
        self,
        user_id: int,
        question_id: int
    ) -> Optional[UserAnswerResponse]:
        """Получить ответ пользователя на конкретный вопрос"""
        stmt = select(UserAnswer).where(
            and_(
                UserAnswer.user_id == user_id,
                UserAnswer.question_id == question_id
            )
        )
        result = await self.db.execute(stmt)
        user_answer = result.scalar_one_or_none()
        if not user_answer:
            return None
        return self._to_response(user_answer)

    async def create(self, user_answer: UserAnswerCreate) -> UserAnswerResponse:
        """Создать новый ответ пользователя"""
        user_answer_obj = UserAnswer(
            user_id=user_answer.user_id,
            question_id=user_answer.question_id,
            selected_answer_id=user_answer.selected_answer_id,
            is_correct=user_answer.is_correct,
            answered_at=datetime.utcnow(),
        )
        self.db.add(user_answer_obj)
        try:
            await self.db.commit()
        except IntegrityError:
            await self.db.rollback()
            raise
        await self.db.refresh(user_answer_obj)
        return self._to_response(user_answer_obj)

    async def update(self, user_answer_id: int, user_answer_data: UserAnswerUpdate) -> Optional[UserAnswerResponse]:
        """Обновить ответ пользователя"""
        user_answer = await self.db.get(UserAnswer, user_answer_id)
        if not user_answer:
            return None
        
        update_data = user_answer_data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            if value is not None:
                setattr(user_answer, key, value)
        
        try:
            await self.db.commit()
        except IntegrityError:
            await self.db.rollback()
            raise
        
        await self.db.refresh(user_answer)
        return self._to_response(user_answer)

    async def delete(self, user_answer_id: int) -> bool:
        """Удалить ответ пользователя"""
        user_answer = await self.db.get(UserAnswer, user_answer_id)
        if not user_answer:
            return False
        await self.db.delete(user_answer)
        try:
            await self.db.commit()
        except IntegrityError:
            await self.db.rollback()
            raise
        return True

    async def delete_by_user_and_question(self, user_id: int, question_id: int) -> bool:
        """Удалить ответ пользователя на конкретный вопрос"""
        stmt = select(UserAnswer).where(
            and_(
                UserAnswer.user_id == user_id,
                UserAnswer.question_id == question_id
            )
        )
        result = await self.db.execute(stmt)
        user_answer = result.scalar_one_or_none()
        if not user_answer:
            return False
        await self.db.delete(user_answer)
        try:
            await self.db.commit()
        except IntegrityError:
            await self.db.rollback()
            raise
        return True

