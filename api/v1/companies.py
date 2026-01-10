from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from core.db import get_db
from core.security import get_current_user
from schemas.company import CompanyCreate, CompanyResponse, CompanyUpdate
from services.company_service import company_service

router = APIRouter(prefix="/companies", tags=["Companies"])


@router.get("/", response_model=List[CompanyResponse])
async def get_companies(
    name: Optional[str] = Query(None, description="Фильтр по названию компании (точное совпадение)"),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    if name:
        # Если указано название, возвращаем одну компанию
        company = await company_service.get_by_name(db, name, current_user)
        return [company]
    return await company_service.get_all(db, current_user)


@router.get("/{company_id}", response_model=CompanyResponse)
async def get_company(
    company_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    return await company_service.get_by_id(db, company_id, current_user)


@router.post("/", response_model=CompanyResponse, status_code=201)
async def create_company(
    company_data: CompanyCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    return await company_service.create(db, company_data.model_dump(), current_user)


@router.patch("/{company_id}", response_model=CompanyResponse)
async def update_company(
    company_id: int,
    update_data: CompanyUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    return await company_service.update(
        db, company_id, update_data.model_dump(exclude_unset=True), current_user
    )


@router.delete("/{company_id}")
async def delete_company(
    company_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    return await company_service.delete(db, company_id, current_user)

