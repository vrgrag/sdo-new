from typing import Optional, List, Dict, Any
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from models.departments import Department


def _to_dict(department: Department) -> Dict[str, Any]:
    return {
        "id": department.id,
        "name": department.name,
        "company_id": department.company_id,
    }


class DepartmentRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all(self) -> List[Dict[str, Any]]:
        stmt = select(Department).order_by(Department.id.asc())
        res = await self.db.execute(stmt)
        departments = res.scalars().all()
        return [_to_dict(d) for d in departments]

    async def get_by_id(self, department_id: int) -> Optional[Dict[str, Any]]:
        department = await self.db.get(Department, department_id)
        if not department:
            return None
        return _to_dict(department)

    async def get_by_company_id(self, company_id: int) -> List[Dict[str, Any]]:
        stmt = select(Department).where(Department.company_id == company_id).order_by(Department.id.asc())
        res = await self.db.execute(stmt)
        departments = res.scalars().all()
        return [_to_dict(d) for d in departments]

    async def get_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        stmt = select(Department).where(Department.name == name).limit(1)
        res = await self.db.execute(stmt)
        department = res.scalar_one_or_none()
        return _to_dict(department) if department else None

    async def get_by_name_and_company(self, name: str, company_id: int) -> Optional[Dict[str, Any]]:
        stmt = select(Department).where(
            Department.name == name,
            Department.company_id == company_id
        ).limit(1)
        res = await self.db.execute(stmt)
        department = res.scalar_one_or_none()
        return _to_dict(department) if department else None

    async def create(self, department_data: Dict[str, Any]) -> Dict[str, Any]:
        department = Department(
            name=department_data["name"],
            company_id=department_data["company_id"]
        )
        self.db.add(department)
        try:
            await self.db.commit()
        except IntegrityError:
            await self.db.rollback()
            raise
        await self.db.refresh(department)
        return _to_dict(department)

    async def update(self, department_id: int, update_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        department = await self.db.get(Department, department_id)
        if not department:
            return None

        for field, value in update_data.items():
            if value is not None:
                setattr(department, field, value)

        try:
            await self.db.commit()
        except IntegrityError:
            await self.db.rollback()
            raise

        await self.db.refresh(department)
        return _to_dict(department)

    async def delete(self, department_id: int) -> bool:
        department = await self.db.get(Department, department_id)
        if not department:
            return False
        await self.db.delete(department)
        await self.db.commit()
        return True

