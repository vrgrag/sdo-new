from typing import List, Dict, Any
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from repositories.mock.company_repository import CompanyRepository


class CompanyService:
    async def _ensure_admin_or_manager(self, db: AsyncSession, current_user: Dict[str, Any]) -> None:
        role = current_user.get("role", "").lower()
        if role not in ("admin", "manager"):
            raise HTTPException(status_code=403, detail="Недостаточно прав")

    async def get_all(self, db: AsyncSession, current_user: Dict[str, Any]) -> List[Dict[str, Any]]:
        await self._ensure_admin_or_manager(db, current_user)
        repo = CompanyRepository(db)
        return await repo.get_all()

    async def get_by_id(self, db: AsyncSession, company_id: int, current_user: Dict[str, Any]) -> Dict[str, Any]:
        await self._ensure_admin_or_manager(db, current_user)
        repo = CompanyRepository(db)
        company = await repo.get_by_id(company_id)
        if not company:
            raise HTTPException(status_code=404, detail="Компания не найдена")
        return company

    async def get_by_name(self, db: AsyncSession, name: str, current_user: Dict[str, Any]) -> Dict[str, Any]:
        await self._ensure_admin_or_manager(db, current_user)
        repo = CompanyRepository(db)
        company = await repo.get_by_name(name)
        if not company:
            raise HTTPException(status_code=404, detail="Компания не найдена")
        return company

    async def create(self, db: AsyncSession, company_data: Dict[str, Any], current_user: Dict[str, Any]) -> Dict[str, Any]:
        await self._ensure_admin_or_manager(db, current_user)
        repo = CompanyRepository(db)

        # Проверка на дубликат
        existing = await repo.get_by_name(company_data["name"])
        if existing:
            raise HTTPException(status_code=400, detail="Компания с таким названием уже существует")

        try:
            return await repo.create(company_data)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Ошибка создания компании: {str(e)}")

    async def update(self, db: AsyncSession, company_id: int, update_data: Dict[str, Any], current_user: Dict[str, Any]) -> Dict[str, Any]:
        await self._ensure_admin_or_manager(db, current_user)
        repo = CompanyRepository(db)

        # Проверка на дубликат если меняется название
        if "name" in update_data and update_data["name"]:
            existing = await repo.get_by_name(update_data["name"])
            if existing and existing["id"] != company_id:
                raise HTTPException(status_code=400, detail="Компания с таким названием уже существует")

        try:
            updated = await repo.update(company_id, update_data)
            if not updated:
                raise HTTPException(status_code=404, detail="Компания не найдена")
            return updated
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Ошибка обновления компании: {str(e)}")

    async def delete(self, db: AsyncSession, company_id: int, current_user: Dict[str, Any]) -> Dict[str, Any]:
        await self._ensure_admin_or_manager(db, current_user)
        repo = CompanyRepository(db)

        # Проверка существования
        existing = await repo.get_by_id(company_id)
        if not existing:
            raise HTTPException(status_code=404, detail="Компания не найдена")

        try:
            success = await repo.delete(company_id)
            if not success:
                raise HTTPException(status_code=404, detail="Компания не найдена")
            return {"detail": "Компания удалена"}
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Ошибка удаления компании: {str(e)}")


company_service = CompanyService()

