from typing import List, Optional, Dict
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from repositories.base import IModuleRepository
from schemas import ModuleResponse, ModuleCreate, ModuleUpdate
from models.modules import Modules


class JsonModuleRepository(IModuleRepository):
    def __init__(self, db: AsyncSession):
        self.db = db

    def _to_response(self, module: Modules) -> ModuleResponse:
        """Преобразует модель Modules в ModuleResponse"""
        return ModuleResponse(
            id=module.id,
            course_id=module.course_id,
            title=module.title,
            description=module.description,
            order=module.order,
            is_published=module.is_published,
            lessons=[]  # уроки будут добавляться отдельно при необходимости
        )

    async def get_by_course(self, course_id: int) -> List[ModuleResponse]:
        stmt = (
            select(Modules)
            .where(Modules.course_id == course_id)
            .order_by(Modules.order.asc())
        )
        res = await self.db.execute(stmt)
        modules = res.scalars().all()
        return [self._to_response(m) for m in modules]

    async def get_by_id(self, module_id: int) -> Optional[ModuleResponse]:
        module = await self.db.get(Modules, module_id)
        if not module:
            return None
        return self._to_response(module)

    async def create(self, module_data: ModuleCreate) -> ModuleResponse:
        module = Modules(
            course_id=module_data.course_id,
            title=module_data.title,
            description=module_data.description,
            order=module_data.order,
            is_published=module_data.is_published,
        )
        self.db.add(module)
        try:
            await self.db.commit()
        except IntegrityError:
            await self.db.rollback()
            raise
        await self.db.refresh(module)
        return self._to_response(module)

    async def update(self, module_id: int, module_data: ModuleUpdate) -> Optional[ModuleResponse]:
        module = await self.db.get(Modules, module_id)
        if not module:
            return None

        update_data = module_data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            if value is not None:
                setattr(module, key, value)

        try:
            await self.db.commit()
        except IntegrityError:
            await self.db.rollback()
            raise

        await self.db.refresh(module)
        return self._to_response(module)

    async def delete(self, module_id: int) -> bool:
        module = await self.db.get(Modules, module_id)
        if not module:
            return False
        await self.db.delete(module)
        await self.db.commit()
        return True
