from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from core.security import get_current_user
from core.roles import UserRole
from core.db import get_db

from schemas import AnswerResponse, AnswerCreate, AnswerUpdate
from services import AnswerService

router = APIRouter(prefix="/answers", tags=["Answers"])


async def get_answer_service(db: AsyncSession = Depends(get_db)) -> AnswerService:
    return AnswerService(db)


@router.get("/", response_model=List[AnswerResponse])
async def get_answers(
    question_id: Optional[int] = Query(None, description="Фильтр по вопросу"),
    service: AnswerService = Depends(get_answer_service),
    current_user: dict = Depends(get_current_user),
):
    """Получить список вариантов ответов"""
    role = current_user["role"]
    
    # Администраторы и менеджеры видят все ответы
    if role in (UserRole.ADMIN.value, UserRole.MANAGER.value):
        return await service.get_all_answers(question_id)
    
    # Тренеры и студенты видят только ответы опубликованных тестов
    # TODO: Добавить проверку доступа через enrollment
    return await service.get_all_answers(question_id)


@router.get("/{answer_id}", response_model=AnswerResponse)
async def get_answer(
    answer_id: int,
    service: AnswerService = Depends(get_answer_service),
    current_user: dict = Depends(get_current_user),
):
    """Получить вариант ответа по ID"""
    return await service.get_answer_by_id(answer_id)


@router.post("/", response_model=AnswerResponse, status_code=201)
async def create_answer(
    answer_data: AnswerCreate,
    service: AnswerService = Depends(get_answer_service),
    current_user: dict = Depends(get_current_user),
):
    """Создать новый вариант ответа"""
    if current_user["role"] not in (UserRole.ADMIN.value, UserRole.MANAGER.value):
        raise HTTPException(status_code=403, detail="Недостаточно прав")
    
    return await service.create_answer(answer_data)


@router.patch("/{answer_id}", response_model=AnswerResponse)
async def update_answer(
    answer_id: int,
    answer_data: AnswerUpdate,
    service: AnswerService = Depends(get_answer_service),
    current_user: dict = Depends(get_current_user),
):
    """Обновить вариант ответа"""
    if current_user["role"] not in (UserRole.ADMIN.value, UserRole.MANAGER.value):
        raise HTTPException(status_code=403, detail="Недостаточно прав")
    
    return await service.update_answer(answer_id, answer_data)


@router.delete("/{answer_id}", status_code=204)
async def delete_answer(
    answer_id: int,
    service: AnswerService = Depends(get_answer_service),
    current_user: dict = Depends(get_current_user),
):
    """Удалить вариант ответа"""
    if current_user["role"] not in (UserRole.ADMIN.value, UserRole.MANAGER.value):
        raise HTTPException(status_code=403, detail="Недостаточно прав")
    
    await service.delete_answer(answer_id)
    return None

