from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from schemas import TestResponse, TestCreate, TestUpdate, TestDetailResponse
from schemas import QuestionResponse, AnswerResponse
from models.tests import Tests
from models.questions import Question
from models.answers import Answer


class TestRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    def _to_response(self, test: Tests) -> TestResponse:
        """Преобразует модель Tests в TestResponse"""
        return TestResponse(
            id=test.id,
            title=test.title,
            description=test.description,
            number_of_attempts=test.number_of_attempts,
            time_limit_minutes=test.time_limit_minutes,
            course_id=test.course_id,
            created_at=test.created_at,
        )

    async def get_all(
        self,
        course_id: Optional[int] = None
    ) -> List[TestResponse]:
        """Получить все тесты, опционально фильтровать по курсу"""
        stmt = select(Tests)
        
        if course_id is not None:
            stmt = stmt.where(Tests.course_id == course_id)
        
        stmt = stmt.order_by(Tests.created_at.desc())
        
        res = await self.db.execute(stmt)
        tests = res.scalars().all()
        return [self._to_response(t) for t in tests]

    async def get_by_id(self, test_id: int) -> Optional[TestResponse]:
        """Получить тест по ID"""
        test = await self.db.get(Tests, test_id)
        if not test:
            return None
        return self._to_response(test)

    async def get_detail(self, test_id: int) -> Optional[TestDetailResponse]:
        """Получить тест со всеми вопросами и ответами"""
        test = await self.db.get(Tests, test_id)
        if not test:
            return None
        
        # Получаем вопросы для теста
        stmt_questions = select(Question).where(Question.test_id == test_id)
        res_questions = await self.db.execute(stmt_questions)
        questions = res_questions.scalars().all()
        
        question_responses = []
        for q in questions:
            # Получаем ответы для вопроса
            stmt_answers = select(Answer).where(Answer.question_id == q.id)
            res_answers = await self.db.execute(stmt_answers)
            answers = res_answers.scalars().all()
            
            question_responses.append(QuestionResponse(
                id=q.id,
                question_text=q.question_text,
                question_type=q.question_type,
                test_id=q.test_id,
                answers=[AnswerResponse(
                    id=a.id,
                    answer_text=a.answer_text,
                    is_correct=a.is_correct,
                    question_id=a.question_id,
                ) for a in answers]
            ))
        
        test_response = self._to_response(test)
        return TestDetailResponse(**test_response.model_dump(), questions=question_responses)

    async def create(self, test: TestCreate) -> TestResponse:
        """Создать новый тест"""
        test_obj = Tests(
            title=test.title,
            description=test.description,
            number_of_attempts=test.number_of_attempts,
            time_limit_minutes=test.time_limit_minutes,
            course_id=test.course_id,
        )
        self.db.add(test_obj)
        try:
            await self.db.commit()
        except IntegrityError:
            await self.db.rollback()
            raise
        await self.db.refresh(test_obj)
        return self._to_response(test_obj)

    async def update(self, test_id: int, test_data: TestUpdate) -> Optional[TestResponse]:
        """Обновить тест"""
        test = await self.db.get(Tests, test_id)
        if not test:
            return None
        
        update_data = test_data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            if value is not None:
                setattr(test, key, value)
        
        try:
            await self.db.commit()
        except IntegrityError:
            await self.db.rollback()
            raise
        
        await self.db.refresh(test)
        return self._to_response(test)

    async def delete(self, test_id: int) -> bool:
        """Удалить тест"""
        test = await self.db.get(Tests, test_id)
        if not test:
            return False
        await self.db.delete(test)
        await self.db.commit()
        return True

