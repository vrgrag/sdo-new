from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from core.db import get_db
from core.security import get_current_user
from schemas.position import PositionCreate, PositionResponse, PositionUpdate
from services.position_service import position_service

router = APIRouter(prefix="/positions", tags=["Positions"])


@router.get("/", response_model=List[PositionResponse])
async def get_positions(
    name: Optional[str] = Query(None, description="Фильтр по названию должности (точное совпадение)"),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    if name:
        # Если указано название, возвращаем одну должность
        position = await position_service.get_by_name(db, name, current_user)
        return [position]
    return await position_service.get_all(db, current_user)


@router.get("/{position_id}", response_model=PositionResponse)
async def get_position(
    position_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    return await position_service.get_by_id(db, position_id, current_user)


@router.post("/", response_model=PositionResponse, status_code=201)
async def create_position(
    position_data: PositionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    return await position_service.create(db, position_data.model_dump(), current_user)


@router.patch("/{position_id}", response_model=PositionResponse)
async def update_position(
    position_id: int,
    update_data: PositionUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    return await position_service.update(
        db, position_id, update_data.model_dump(exclude_unset=True), current_user
    )


@router.delete("/{position_id}")
async def delete_position(
    position_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    return await position_service.delete(db, position_id, current_user)

