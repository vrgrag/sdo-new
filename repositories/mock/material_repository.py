from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from schemas import MaterialResponse, MaterialCreate, MaterialUpdate
from models.materials import Materials


class MaterialRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    def _to_response(self, material: Materials) -> MaterialResponse:
        """Преобразует модель Materials в MaterialResponse"""
        return MaterialResponse(
            id=material.id,
            title=material.title,
            number_of_pages=material.number_of_pages,
            description=material.description,
            file_path=material.file_path,
            course_id=material.course_id,
        )

    async def get_all(
        self,
        course_id: Optional[int] = None
    ) -> List[MaterialResponse]:
        """Получить все материалы, опционально фильтровать по курсу"""
        stmt = select(Materials)
        
        if course_id is not None:
            stmt = stmt.where(Materials.course_id == course_id)
        
        res = await self.db.execute(stmt)
        materials = res.scalars().all()
        return [self._to_response(m) for m in materials]

    async def get_by_id(self, material_id: int) -> Optional[MaterialResponse]:
        """Получить материал по ID"""
        material = await self.db.get(Materials, material_id)
        if not material:
            return None
        return self._to_response(material)

    async def create(self, material: MaterialCreate) -> MaterialResponse:
        """Создать новый материал"""
        material_obj = Materials(
            title=material.title,
            number_of_pages=material.number_of_pages,
            description=material.description,
            file_path=material.file_path,
            course_id=material.course_id,
        )
        self.db.add(material_obj)
        try:
            await self.db.commit()
        except IntegrityError:
            await self.db.rollback()
            raise
        await self.db.refresh(material_obj)
        return self._to_response(material_obj)

    async def update(self, material_id: int, material_data: MaterialUpdate) -> Optional[MaterialResponse]:
        """Обновить материал"""
        material = await self.db.get(Materials, material_id)
        if not material:
            return None
        
        update_data = material_data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            if value is not None:
                setattr(material, key, value)
        
        try:
            await self.db.commit()
        except IntegrityError:
            await self.db.rollback()
            raise
        
        await self.db.refresh(material)
        return self._to_response(material)

    async def delete(self, material_id: int) -> bool:
        """Удалить материал"""
        material = await self.db.get(Materials, material_id)
        if not material:
            return False
        await self.db.delete(material)
        try:
            await self.db.commit()
        except IntegrityError:
            await self.db.rollback()
            raise
        return True

