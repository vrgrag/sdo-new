from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from core.security import get_current_user
from core.roles import UserRole
from core.db import get_db

from schemas import TestResponse, TestCreate, TestUpdate, TestDetailResponse
from services import TestService

router = APIRouter(prefix="/tests", tags=["Tests"])


async def get_test_service(db: AsyncSession = Depends(get_db)) -> TestService:
    return TestService(db)


@router.get("/", response_model=List[TestResponse])
async def get_tests(
    course_id: Optional[int] = Query(None, description="Фильтр по курсу"),
    service: TestService = Depends(get_test_service),
    current_user: dict = Depends(get_current_user),
):
    """Получить список тестов"""
    role = current_user["role"]
    user_id = current_user["id"]
    
    # Администраторы и менеджеры видят все тесты
    if role in (UserRole.ADMIN.value, UserRole.MANAGER.value):
        return await service.get_all_tests(course_id)
    
    # Тренеры видят тесты только своих курсов
    # Студенты видят только опубликованные тесты своих курсов
    # TODO: Добавить проверку доступа через enrollment
    return await service.get_all_tests(course_id)


@router.get("/{test_id}", response_model=TestResponse)
async def get_test(
    test_id: int,
    service: TestService = Depends(get_test_service),
    current_user: dict = Depends(get_current_user),
):
    """Получить тест по ID"""
    return await service.get_test_by_id(test_id)


@router.get("/{test_id}/detail", response_model=TestDetailResponse)
async def get_test_detail(
    test_id: int,
    service: TestService = Depends(get_test_service),
    current_user: dict = Depends(get_current_user),
):
    """Получить тест со всеми вопросами и ответами"""
    return await service.get_test_detail(test_id)


@router.post("/", response_model=TestResponse, status_code=201)
async def create_test(
    test_data: TestCreate,
    service: TestService = Depends(get_test_service),
    current_user: dict = Depends(get_current_user),
):
    """Создать новый тест"""
    if current_user["role"] not in (UserRole.ADMIN.value, UserRole.MANAGER.value):
        raise HTTPException(status_code=403, detail="Недостаточно прав")
    
    return await service.create_test(test_data)


@router.patch("/{test_id}", response_model=TestResponse)
async def update_test(
    test_id: int,
    test_data: TestUpdate,
    service: TestService = Depends(get_test_service),
    current_user: dict = Depends(get_current_user),
):
    """Обновить тест"""
    if current_user["role"] not in (UserRole.ADMIN.value, UserRole.MANAGER.value):
        raise HTTPException(status_code=403, detail="Недостаточно прав")
    
    return await service.update_test(test_id, test_data)


@router.delete("/{test_id}", status_code=204)
async def delete_test(
    test_id: int,
    service: TestService = Depends(get_test_service),
    current_user: dict = Depends(get_current_user),
):
    """Удалить тест"""
    if current_user["role"] not in (UserRole.ADMIN.value, UserRole.MANAGER.value):
        raise HTTPException(status_code=403, detail="Недостаточно прав")
    
    await service.delete_test(test_id)
    return None

