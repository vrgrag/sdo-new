from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from core.security import get_current_user
from core.roles import UserRole
from core.db import get_db

from schemas import TaskResponse, TaskCreate, TaskUpdate
from services import TaskService

router = APIRouter(prefix="/tasks", tags=["Tasks"])


async def get_task_service(db: AsyncSession = Depends(get_db)) -> TaskService:
    return TaskService(db)


@router.get("/", response_model=List[TaskResponse])
async def get_tasks(
    course_id: Optional[int] = Query(None, description="Фильтр по курсу"),
    user_id: Optional[int] = Query(None, description="Фильтр по создателю задания"),
    assigned_to_user_id: Optional[int] = Query(None, description="Фильтр по назначенному пользователю"),
    service: TaskService = Depends(get_task_service),
    current_user: dict = Depends(get_current_user),
):
    """Получить список заданий"""
    role = current_user["role"]
    current_user_id = current_user["id"]
    
    # Администраторы и менеджеры видят все задания
    if role in (UserRole.ADMIN.value, UserRole.MANAGER.value):
        return await service.get_all_tasks(course_id, user_id, assigned_to_user_id)
    
    # Тренеры видят задания своих курсов и свои задания
    if role == UserRole.TRAINER.value:
        # TODO: Добавить проверку через enrollment
        return await service.get_all_tasks(course_id, current_user_id, assigned_to_user_id)
    
    # Студенты видят только назначенные им задания и свои созданные
    if role == UserRole.STUDENT.value:
        # Студенты не могут фильтровать по другим пользователям
        if user_id is not None and user_id != current_user_id:
            raise HTTPException(status_code=403, detail="Недостаточно прав")
        if assigned_to_user_id is not None and assigned_to_user_id != current_user_id:
            raise HTTPException(status_code=403, detail="Недостаточно прав")
        # Показываем задания назначенные студенту или созданные им
        return await service.get_all_tasks(course_id, current_user_id, current_user_id)
    
    return await service.get_all_tasks(course_id, user_id, assigned_to_user_id)


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: int,
    service: TaskService = Depends(get_task_service),
    current_user: dict = Depends(get_current_user),
):
    """Получить задание по ID"""
    role = current_user["role"]
    current_user_id = current_user["id"]
    
    task = await service.get_task_by_id(task_id)
    
    # Студенты могут видеть только назначенные им задания или свои созданные
    if role == UserRole.STUDENT.value:
        if task.assigned_to_user_id != current_user_id and task.created_by_id != current_user_id:
            raise HTTPException(status_code=403, detail="Недостаточно прав")
    
    return task


@router.post("/", response_model=TaskResponse, status_code=201)
async def create_task(
    task_data: TaskCreate,
    service: TaskService = Depends(get_task_service),
    current_user: dict = Depends(get_current_user),
):
    """Создать новое задание"""
    role = current_user["role"]
    current_user_id = current_user["id"]
    
    # Студенты могут создавать задания только для себя
    if role == UserRole.STUDENT.value:
        if task_data.assigned_to_user_id is not None and task_data.assigned_to_user_id != current_user_id:
            raise HTTPException(status_code=403, detail="Студенты могут создавать задания только для себя")
    
    return await service.create_task(task_data, current_user_id)


@router.patch("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: int,
    task_data: TaskUpdate,
    service: TaskService = Depends(get_task_service),
    current_user: dict = Depends(get_current_user),
):
    """Обновить задание"""
    role = current_user["role"]
    current_user_id = current_user["id"]
    
    # Проверяем доступ
    existing_task = await service.get_task_by_id(task_id)
    
    # Студенты могут обновлять только свои задания
    if role == UserRole.STUDENT.value:
        if existing_task.created_by_id != current_user_id:
            raise HTTPException(status_code=403, detail="Недостаточно прав")
    
    # Тренеры могут обновлять задания своих курсов
    if role == UserRole.TRAINER.value:
        # TODO: Добавить проверку через enrollment
        if existing_task.created_by_id != current_user_id:
            raise HTTPException(status_code=403, detail="Недостаточно прав")
    
    return await service.update_task(task_id, task_data)


@router.delete("/{task_id}", status_code=204)
async def delete_task(
    task_id: int,
    service: TaskService = Depends(get_task_service),
    current_user: dict = Depends(get_current_user),
):
    """Удалить задание"""
    role = current_user["role"]
    current_user_id = current_user["id"]
    
    # Проверяем доступ
    existing_task = await service.get_task_by_id(task_id)
    
    # Студенты могут удалять только свои задания
    if role == UserRole.STUDENT.value:
        if existing_task.created_by_id != current_user_id:
            raise HTTPException(status_code=403, detail="Недостаточно прав")
    
    # Тренеры могут удалять задания своих курсов
    if role == UserRole.TRAINER.value:
        # TODO: Добавить проверку через enrollment
        if existing_task.created_by_id != current_user_id:
            raise HTTPException(status_code=403, detail="Недостаточно прав")
    
    await service.delete_task(task_id)
    return None

