from typing import List, Dict, Any, Optional
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from repositories.mock.department_repository import DepartmentRepository
from repositories.mock.company_repository import CompanyRepository


class DepartmentService:
    async def _ensure_admin_or_manager(self, db: AsyncSession, current_user: Dict[str, Any]) -> None:
        role = current_user.get("role", "").lower()
        if role not in ("admin", "manager"):
            raise HTTPException(status_code=403, detail="Недостаточно прав")

    async def get_all(self, db: AsyncSession, current_user: Dict[str, Any], company_id: Optional[int] = None) -> List[Dict[str, Any]]:
        await self._ensure_admin_or_manager(db, current_user)
        repo = DepartmentRepository(db)

        if company_id is not None:
            # Проверяем существование компании
            company_repo = CompanyRepository(db)
            company = await company_repo.get_by_id(company_id)
            if not company:
                raise HTTPException(status_code=404, detail="Компания не найдена")
            return await repo.get_by_company_id(company_id)

        return await repo.get_all()

    async def get_by_id(self, db: AsyncSession, department_id: int, current_user: Dict[str, Any]) -> Dict[str, Any]:
        await self._ensure_admin_or_manager(db, current_user)
        repo = DepartmentRepository(db)
        department = await repo.get_by_id(department_id)
        if not department:
            raise HTTPException(status_code=404, detail="Отдел не найден")
        return department

    async def get_by_name(self, db: AsyncSession, name: str, company_id: int, current_user: Dict[str, Any]) -> Dict[str, Any]:
        await self._ensure_admin_or_manager(db, current_user)
        repo = DepartmentRepository(db)
        department = await repo.get_by_name_and_company(name, company_id)
        if not department:
            raise HTTPException(status_code=404, detail="Отдел не найден")
        return department

    async def create(self, db: AsyncSession, department_data: Dict[str, Any], current_user: Dict[str, Any]) -> Dict[str, Any]:
        await self._ensure_admin_or_manager(db, current_user)
        repo = DepartmentRepository(db)

        # Проверка компании (обязательна)
        company_id = department_data.get("company_id")
        if not company_id:
            raise HTTPException(status_code=400, detail="company_id обязателен")

        company_repo = CompanyRepository(db)
        company = await company_repo.get_by_id(company_id)
        if not company:
            raise HTTPException(status_code=404, detail="Компания не найдена")

        # Проверка на дубликат (по названию и компании)
        existing = await repo.get_by_name_and_company(department_data["name"], company_id)
        if existing:
            raise HTTPException(status_code=400, detail="Отдел с таким названием уже существует в этой компании")

        try:
            return await repo.create(department_data)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Ошибка создания отдела: {str(e)}")

    async def update(self, db: AsyncSession, department_id: int, update_data: Dict[str, Any], current_user: Dict[str, Any]) -> Dict[str, Any]:
        await self._ensure_admin_or_manager(db, current_user)
        repo = DepartmentRepository(db)

        # Проверка компании если меняется (company_id всегда должен быть валидным если указан)
        if "company_id" in update_data and update_data["company_id"] is not None:
            company_repo = CompanyRepository(db)
            company = await company_repo.get_by_id(update_data["company_id"])
            if not company:
                raise HTTPException(status_code=404, detail="Компания не найдена")

        # Проверка на дубликат если меняется название
        # Получаем текущий отдел для проверки
        current_department = await repo.get_by_id(department_id)
        if not current_department:
            raise HTTPException(status_code=404, detail="Отдел не найден")
        
        # Определяем company_id для проверки (новый если меняется, иначе текущий)
        check_company_id = update_data.get("company_id") if "company_id" in update_data and update_data["company_id"] is not None else current_department["company_id"]
        
        if "name" in update_data and update_data["name"]:
            existing = await repo.get_by_name_and_company(update_data["name"], check_company_id)
            if existing and existing["id"] != department_id:
                raise HTTPException(status_code=400, detail="Отдел с таким названием уже существует в этой компании")

        try:
            updated = await repo.update(department_id, update_data)
            if not updated:
                raise HTTPException(status_code=404, detail="Отдел не найден")
            return updated
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Ошибка обновления отдела: {str(e)}")

    async def delete(self, db: AsyncSession, department_id: int, current_user: Dict[str, Any]) -> Dict[str, Any]:
        await self._ensure_admin_or_manager(db, current_user)
        repo = DepartmentRepository(db)

        # Проверка существования
        existing = await repo.get_by_id(department_id)
        if not existing:
            raise HTTPException(status_code=404, detail="Отдел не найден")

        try:
            success = await repo.delete(department_id)
            if not success:
                raise HTTPException(status_code=404, detail="Отдел не найден")
            return {"detail": "Отдел удален"}
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Ошибка удаления отдела: {str(e)}")


department_service = DepartmentService()

