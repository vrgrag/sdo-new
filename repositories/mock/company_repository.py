from typing import Optional, List, Dict, Any
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from models.companies import Company


def _to_dict(company: Company) -> Dict[str, Any]:
    return {
        "id": company.id,
        "name": company.name,
    }


class CompanyRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all(self) -> List[Dict[str, Any]]:
        stmt = select(Company).order_by(Company.id.asc())
        res = await self.db.execute(stmt)
        companies = res.scalars().all()
        return [_to_dict(c) for c in companies]

    async def get_by_id(self, company_id: int) -> Optional[Dict[str, Any]]:
        company = await self.db.get(Company, company_id)
        if not company:
            return None
        return _to_dict(company)

    async def get_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        stmt = select(Company).where(Company.name == name).limit(1)
        res = await self.db.execute(stmt)
        company = res.scalar_one_or_none()
        return _to_dict(company) if company else None

    async def create(self, company_data: Dict[str, Any]) -> Dict[str, Any]:
        company = Company(name=company_data["name"])
        self.db.add(company)
        try:
            await self.db.commit()
        except IntegrityError:
            await self.db.rollback()
            raise
        await self.db.refresh(company)
        return _to_dict(company)

    async def update(self, company_id: int, update_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        company = await self.db.get(Company, company_id)
        if not company:
            return None

        for field, value in update_data.items():
            if value is not None:
                setattr(company, field, value)

        try:
            await self.db.commit()
        except IntegrityError:
            await self.db.rollback()
            raise

        await self.db.refresh(company)
        return _to_dict(company)

    async def delete(self, company_id: int) -> bool:
        company = await self.db.get(Company, company_id)
        if not company:
            return False
        await self.db.delete(company)
        await self.db.commit()
        return True

