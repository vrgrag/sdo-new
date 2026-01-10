from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from core.security import get_current_user
from core.roles import UserRole
from core.db import get_db

from schemas import MaterialResponse, MaterialCreate, MaterialUpdate
from services import MaterialService

router = APIRouter(prefix="/materials", tags=["Materials"])


async def get_material_service(db: AsyncSession = Depends(get_db)) -> MaterialService:
    return MaterialService(db)


@router.get("/", response_model=List[MaterialResponse])
async def get_materials(
    course_id: Optional[int] = Query(None, description="Фильтр по курсу"),
    service: MaterialService = Depends(get_material_service),
    current_user: dict = Depends(get_current_user),
):
    """Получить список материалов"""
    role = current_user["role"]
    
    # Администраторы и менеджеры видят все материалы
    if role in (UserRole.ADMIN.value, UserRole.MANAGER.value):
        return await service.get_all_materials(course_id)
    
    # Тренеры видят материалы своих курсов
    # Студенты видят материалы своих курсов
    # TODO: Добавить проверку доступа через enrollment
    return await service.get_all_materials(course_id)


@router.get("/{material_id}", response_model=MaterialResponse)
async def get_material(
    material_id: int,
    service: MaterialService = Depends(get_material_service),
    current_user: dict = Depends(get_current_user),
):
    """Получить материал по ID"""
    return await service.get_material_by_id(material_id)


@router.post("/", response_model=MaterialResponse, status_code=201)
async def create_material(
    material_data: MaterialCreate,
    service: MaterialService = Depends(get_material_service),
    current_user: dict = Depends(get_current_user),
):
    """Создать новый материал"""
    if current_user["role"] not in (UserRole.ADMIN.value, UserRole.MANAGER.value, UserRole.TRAINER.value):
        raise HTTPException(status_code=403, detail="Недостаточно прав")
    
    # Тренеры могут создавать материалы только для своих курсов
    if current_user["role"] == UserRole.TRAINER.value:
        # TODO: Добавить проверку через enrollment
        pass
    
    return await service.create_material(material_data)


@router.patch("/{material_id}", response_model=MaterialResponse)
async def update_material(
    material_id: int,
    material_data: MaterialUpdate,
    service: MaterialService = Depends(get_material_service),
    current_user: dict = Depends(get_current_user),
):
    """Обновить материал"""
    if current_user["role"] not in (UserRole.ADMIN.value, UserRole.MANAGER.value, UserRole.TRAINER.value):
        raise HTTPException(status_code=403, detail="Недостаточно прав")
    
    # Тренеры могут обновлять материалы только своих курсов
    if current_user["role"] == UserRole.TRAINER.value:
        # TODO: Добавить проверку через enrollment
        pass
    
    return await service.update_material(material_id, material_data)


@router.delete("/{material_id}", status_code=204)
async def delete_material(
    material_id: int,
    service: MaterialService = Depends(get_material_service),
    current_user: dict = Depends(get_current_user),
):
    """Удалить материал"""
    if current_user["role"] not in (UserRole.ADMIN.value, UserRole.MANAGER.value, UserRole.TRAINER.value):
        raise HTTPException(status_code=403, detail="Недостаточно прав")
    
    # Тренеры могут удалять материалы только своих курсов
    if current_user["role"] == UserRole.TRAINER.value:
        # TODO: Добавить проверку через enrollment
        pass
    
    await service.delete_material(material_id)
    return None

