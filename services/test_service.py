# services/test_service.py
from typing import List, Optional
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from schemas import TestResponse, TestCreate, TestUpdate, TestDetailResponse
from repositories.mock.test_repository import TestRepository
from repositories.mock.question_repository import QuestionRepository


class TestService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.test_repo = TestRepository(db)
        self.question_repo = QuestionRepository(db)

    async def get_all_tests(
        self,
        course_id: Optional[int] = None
    ) -> List[TestResponse]:
        """Получить все тесты, опционально фильтровать по курсу"""
        return await self.test_repo.get_all(course_id)

    async def get_test_by_id(self, test_id: int) -> TestResponse:
        """Получить тест по ID"""
        test = await self.test_repo.get_by_id(test_id)
        if not test:
            raise HTTPException(status_code=404, detail="Тест не найден")
        return test

    async def get_test_detail(self, test_id: int) -> TestDetailResponse:
        """Получить тест со всеми вопросами и ответами"""
        test_detail = await self.test_repo.get_detail(test_id)
        if not test_detail:
            raise HTTPException(status_code=404, detail="Тест не найден")
        return test_detail

    async def create_test(self, test_data: TestCreate) -> TestResponse:
        """Создать новый тест"""
        return await self.test_repo.create(test_data)

    async def update_test(self, test_id: int, test_data: TestUpdate) -> TestResponse:
        """Обновить тест"""
        updated = await self.test_repo.update(test_id, test_data)
        if not updated:
            raise HTTPException(status_code=404, detail="Тест не найден")
        return updated

    async def delete_test(self, test_id: int) -> bool:
        """Удалить тест"""
        success = await self.test_repo.delete(test_id)
        if not success:
            raise HTTPException(status_code=404, detail="Тест не найден")
        return success

