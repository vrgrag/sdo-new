# services/task_service.py
from typing import List, Optional
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from schemas import TaskResponse, TaskCreate, TaskUpdate
from repositories.mock.task_repository import TaskRepository
from repositories.mock.course_repository import JsonCourseRepository


class TaskService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.task_repo = TaskRepository(db)
        self.course_repo = JsonCourseRepository(db)

    async def get_all_tasks(
        self,
        course_id: Optional[int] = None,
        user_id: Optional[int] = None,
        assigned_to_user_id: Optional[int] = None
    ) -> List[TaskResponse]:
        """Получить все задания, опционально фильтровать"""
        return await self.task_repo.get_all(course_id, user_id, assigned_to_user_id)

    async def get_task_by_id(self, task_id: int) -> TaskResponse:
        """Получить задание по ID"""
        task = await self.task_repo.get_by_id(task_id)
        if not task:
            raise HTTPException(status_code=404, detail="Задание не найдено")
        return task

    async def create_task(self, task_data: TaskCreate, created_by_id: int) -> TaskResponse:
        """Создать новое задание"""
        # Проверяем что курс существует
        course = await self.course_repo.get_by_id(task_data.course_id)
        if not course:
            raise HTTPException(status_code=404, detail="Курс не найден")
        
        return await self.task_repo.create(task_data, created_by_id)

    async def update_task(self, task_id: int, task_data: TaskUpdate) -> TaskResponse:
        """Обновить задание"""
        if task_data.course_id:
            # Проверяем что курс существует
            course = await self.course_repo.get_by_id(task_data.course_id)
            if not course:
                raise HTTPException(status_code=404, detail="Курс не найден")
        
        updated = await self.task_repo.update(task_id, task_data)
        if not updated:
            raise HTTPException(status_code=404, detail="Задание не найдено")
        return updated

    async def delete_task(self, task_id: int) -> bool:
        """Удалить задание"""
        success = await self.task_repo.delete(task_id)
        if not success:
            raise HTTPException(status_code=404, detail="Задание не найдено")
        return success

