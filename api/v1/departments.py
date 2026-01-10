from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from core.db import get_db
from core.security import get_current_user
from schemas.department import DepartmentCreate, DepartmentResponse, DepartmentUpdate
from services.department_service import department_service

router = APIRouter(prefix="/departments", tags=["Departments"])


@router.get("/", response_model=List[DepartmentResponse])
async def get_departments(
    name: Optional[str] = Query(None, description="Фильтр по названию отдела (точное совпадение)"),
    company_id: Optional[int] = Query(None, description="Фильтр по компании (обязателен, если указано название)"),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    if name:
        # Если указано название, возвращаем один отдел
        if not company_id:
            raise HTTPException(status_code=400, detail="company_id обязателен при поиске по названию")
        department = await department_service.get_by_name(db, name, company_id, current_user)
        return [department]
    return await department_service.get_all(db, current_user, company_id=company_id)


@router.get("/{department_id}", response_model=DepartmentResponse)
async def get_department(
    department_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    return await department_service.get_by_id(db, department_id, current_user)


@router.post("/", response_model=DepartmentResponse, status_code=201)
async def create_department(
    department_data: DepartmentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    return await department_service.create(db, department_data.model_dump(), current_user)


@router.patch("/{department_id}", response_model=DepartmentResponse)
async def update_department(
    department_id: int,
    update_data: DepartmentUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    return await department_service.update(
        db, department_id, update_data.model_dump(exclude_unset=True), current_user
    )


@router.delete("/{department_id}")
async def delete_department(
    department_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    return await department_service.delete(db, department_id, current_user)

