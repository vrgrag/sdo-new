from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from core.security import get_current_user
from core.roles import UserRole
from core.db import get_db

from schemas import UserAnswerResponse, UserAnswerCreate, UserAnswerUpdate
from services import UserAnswerService

router = APIRouter(prefix="/user-answers", tags=["UserAnswers"])


async def get_user_answer_service(db: AsyncSession = Depends(get_db)) -> UserAnswerService:
    return UserAnswerService(db)


@router.get("/", response_model=List[UserAnswerResponse])
async def get_user_answers(
    user_id: Optional[int] = Query(None, description="Фильтр по пользователю"),
    question_id: Optional[int] = Query(None, description="Фильтр по вопросу"),
    test_id: Optional[int] = Query(None, description="Фильтр по тесту"),
    service: UserAnswerService = Depends(get_user_answer_service),
    current_user: dict = Depends(get_current_user),
):
    """Получить список ответов пользователей"""
    role = current_user["role"]
    current_user_id = current_user["id"]
    
    # Администраторы и менеджеры видят все ответы
    if role in (UserRole.ADMIN.value, UserRole.MANAGER.value):
        return await service.get_all_user_answers(user_id, question_id, test_id)
    
    # Тренеры видят ответы только на свои тесты
    # Студенты видят только свои ответы
    if role == UserRole.STUDENT.value:
        if user_id is not None and user_id != current_user_id:
            raise HTTPException(status_code=403, detail="Недостаточно прав")
        return await service.get_all_user_answers(current_user_id, question_id, test_id)
    
    # Тренеры - TODO: Добавить проверку через enrollment
    return await service.get_all_user_answers(user_id, question_id, test_id)


@router.get("/{user_answer_id}", response_model=UserAnswerResponse)
async def get_user_answer(
    user_answer_id: int,
    service: UserAnswerService = Depends(get_user_answer_service),
    current_user: dict = Depends(get_current_user),
):
    """Получить ответ пользователя по ID"""
    role = current_user["role"]
    current_user_id = current_user["id"]
    
    user_answer = await service.get_user_answer_by_id(user_answer_id)
    
    # Студенты могут видеть только свои ответы
    if role == UserRole.STUDENT.value:
        if user_answer.user_id != current_user_id:
            raise HTTPException(status_code=403, detail="Недостаточно прав")
    
    return user_answer


@router.post("/", response_model=UserAnswerResponse, status_code=201)
async def create_user_answer(
    user_answer_data: UserAnswerCreate,
    service: UserAnswerService = Depends(get_user_answer_service),
    current_user: dict = Depends(get_current_user),
):
    """Создать ответ пользователя на вопрос"""
    role = current_user["role"]
    current_user_id = current_user["id"]
    
    # Студенты могут создавать только свои ответы
    if role == UserRole.STUDENT.value:
        if user_answer_data.user_id != current_user_id:
            raise HTTPException(status_code=403, detail="Недостаточно прав")
    
    # Администраторы и менеджеры могут создавать ответы для любого пользователя
    return await service.create_user_answer(user_answer_data)


@router.patch("/{user_answer_id}", response_model=UserAnswerResponse)
async def update_user_answer(
    user_answer_id: int,
    user_answer_data: UserAnswerUpdate,
    service: UserAnswerService = Depends(get_user_answer_service),
    current_user: dict = Depends(get_current_user),
):
    """Обновить ответ пользователя"""
    role = current_user["role"]
    current_user_id = current_user["id"]
    
    # Проверяем доступ
    existing_answer = await service.get_user_answer_by_id(user_answer_id)
    
    # Студенты могут обновлять только свои ответы
    if role == UserRole.STUDENT.value:
        if existing_answer.user_id != current_user_id:
            raise HTTPException(status_code=403, detail="Недостаточно прав")
    
    return await service.update_user_answer(user_answer_id, user_answer_data)


@router.delete("/{user_answer_id}", status_code=204)
async def delete_user_answer(
    user_answer_id: int,
    service: UserAnswerService = Depends(get_user_answer_service),
    current_user: dict = Depends(get_current_user),
):
    """Удалить ответ пользователя"""
    role = current_user["role"]
    current_user_id = current_user["id"]
    
    # Проверяем доступ
    existing_answer = await service.get_user_answer_by_id(user_answer_id)
    
    # Студенты могут удалять только свои ответы
    if role == UserRole.STUDENT.value:
        if existing_answer.user_id != current_user_id:
            raise HTTPException(status_code=403, detail="Недостаточно прав")
    
    await service.delete_user_answer(user_answer_id)
    return None

