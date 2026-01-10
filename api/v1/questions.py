from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from core.security import get_current_user
from core.roles import UserRole
from core.db import get_db

from schemas import QuestionResponse, QuestionCreate, QuestionUpdate
from services import QuestionService

router = APIRouter(prefix="/questions", tags=["Questions"])


async def get_question_service(db: AsyncSession = Depends(get_db)) -> QuestionService:
    return QuestionService(db)


@router.get("/", response_model=List[QuestionResponse])
async def get_questions(
    test_id: Optional[int] = Query(None, description="Фильтр по тесту"),
    service: QuestionService = Depends(get_question_service),
    current_user: dict = Depends(get_current_user),
):
    """Получить список вопросов"""
    role = current_user["role"]
    
    # Администраторы и менеджеры видят все вопросы
    if role in (UserRole.ADMIN.value, UserRole.MANAGER.value):
        return await service.get_all_questions(test_id)
    
    # Тренеры и студенты видят только вопросы опубликованных тестов
    # TODO: Добавить проверку доступа через enrollment
    return await service.get_all_questions(test_id)


@router.get("/{question_id}", response_model=QuestionResponse)
async def get_question(
    question_id: int,
    service: QuestionService = Depends(get_question_service),
    current_user: dict = Depends(get_current_user),
):
    """Получить вопрос по ID"""
    return await service.get_question_by_id(question_id)


@router.post("/", response_model=QuestionResponse, status_code=201)
async def create_question(
    question_data: QuestionCreate,
    service: QuestionService = Depends(get_question_service),
    current_user: dict = Depends(get_current_user),
):
    """Создать новый вопрос с ответами"""
    if current_user["role"] not in (UserRole.ADMIN.value, UserRole.MANAGER.value):
        raise HTTPException(status_code=403, detail="Недостаточно прав")
    
    return await service.create_question(question_data)


@router.patch("/{question_id}", response_model=QuestionResponse)
async def update_question(
    question_id: int,
    question_data: QuestionUpdate,
    service: QuestionService = Depends(get_question_service),
    current_user: dict = Depends(get_current_user),
):
    """Обновить вопрос"""
    if current_user["role"] not in (UserRole.ADMIN.value, UserRole.MANAGER.value):
        raise HTTPException(status_code=403, detail="Недостаточно прав")
    
    return await service.update_question(question_id, question_data)


@router.delete("/{question_id}", status_code=204)
async def delete_question(
    question_id: int,
    service: QuestionService = Depends(get_question_service),
    current_user: dict = Depends(get_current_user),
):
    """Удалить вопрос"""
    if current_user["role"] not in (UserRole.ADMIN.value, UserRole.MANAGER.value):
        raise HTTPException(status_code=403, detail="Недостаточно прав")
    
    await service.delete_question(question_id)
    return None

