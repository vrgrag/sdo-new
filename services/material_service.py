# services/material_service.py
from typing import List, Optional
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from schemas import MaterialResponse, MaterialCreate, MaterialUpdate
from repositories.mock.material_repository import MaterialRepository
from repositories.mock.course_repository import JsonCourseRepository
from core.config import settings


class MaterialService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.material_repo = MaterialRepository(db)
        self.course_repo = JsonCourseRepository(db)

    async def get_all_materials(
        self,
        course_id: Optional[int] = None
    ) -> List[MaterialResponse]:
        """Получить все материалы, опционально фильтровать по курсу"""
        materials = await self.material_repo.get_all(course_id)
        return [self._enrich_material(m) for m in materials]

    async def get_material_by_id(self, material_id: int) -> MaterialResponse:
        """Получить материал по ID"""
        material = await self.material_repo.get_by_id(material_id)
        if not material:
            raise HTTPException(status_code=404, detail="Материал не найден")
        return self._enrich_material(material)

    async def create_material(self, material_data: MaterialCreate) -> MaterialResponse:
        """Создать новый материал"""
        # Проверяем что курс существует
        course = await self.course_repo.get_by_id(material_data.course_id)
        if not course:
            raise HTTPException(status_code=404, detail="Курс не найден")
        
        material = await self.material_repo.create(material_data)
        return self._enrich_material(material)

    async def update_material(self, material_id: int, material_data: MaterialUpdate) -> MaterialResponse:
        """Обновить материал"""
        if material_data.course_id:
            # Проверяем что курс существует
            course = await self.course_repo.get_by_id(material_data.course_id)
            if not course:
                raise HTTPException(status_code=404, detail="Курс не найден")
        
        updated = await self.material_repo.update(material_id, material_data)
        if not updated:
            raise HTTPException(status_code=404, detail="Материал не найден")
        return self._enrich_material(updated)

    async def delete_material(self, material_id: int) -> bool:
        """Удалить материал"""
        success = await self.material_repo.delete(material_id)
        if not success:
            raise HTTPException(status_code=404, detail="Материал не найден")
        return success

    def _enrich_material(self, material: MaterialResponse) -> MaterialResponse:
        """Обогащает материал полным URL файла"""
        if not material or not material.file_path:
            return material
        
        file_path = material.file_path
        # Если путь начинается с /uploads/ или /static/, добавляем SERVER_URL
        if file_path.startswith("/uploads/") or file_path.startswith("/static/"):
            material.file_path = f"{settings.SERVER_URL}{file_path}"
        
        return material

