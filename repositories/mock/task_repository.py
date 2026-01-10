from typing import List, Optional
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from schemas import TaskResponse, TaskCreate, TaskUpdate
from models.tasks import Tasks


class TaskRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    def _to_response(self, task: Tasks) -> TaskResponse:
        """Преобразует модель Tasks в TaskResponse"""
        return TaskResponse(
            id=task.id,
            title=task.title,
            description=task.description,
            status=task.status,
            deadline=task.deadline,
            assigned_to_user_id=task.assigned_to_user_id,
            course_id=task.course_id,
            date_created=task.date_created,
            created_at=task.created_at,
            created_by_id=task.created_by_id,
        )

    async def get_all(
        self,
        course_id: Optional[int] = None,
        user_id: Optional[int] = None,
        assigned_to_user_id: Optional[int] = None
    ) -> List[TaskResponse]:
        """Получить все задания, опционально фильтровать по курсу и пользователю"""
        stmt = select(Tasks)
        
        conditions = []
        if course_id is not None:
            conditions.append(Tasks.course_id == course_id)
        if user_id is not None:
            # Задания созданные пользователем
            conditions.append(Tasks.created_by_id == user_id)
        if assigned_to_user_id is not None:
            # Задания назначенные пользователю
            conditions.append(Tasks.assigned_to_user_id == assigned_to_user_id)
        
        if conditions:
            stmt = stmt.where(and_(*conditions)) if len(conditions) > 1 else stmt.where(conditions[0])
        
        stmt = stmt.order_by(Tasks.created_at.desc())
        
        res = await self.db.execute(stmt)
        tasks = res.scalars().all()
        return [self._to_response(t) for t in tasks]

    async def get_by_id(self, task_id: int) -> Optional[TaskResponse]:
        """Получить задание по ID"""
        task = await self.db.get(Tasks, task_id)
        if not task:
            return None
        return self._to_response(task)

    async def create(self, task: TaskCreate, created_by_id: int) -> TaskResponse:
        """Создать новое задание"""
        from datetime import datetime
        
        task_obj = Tasks(
            title=task.title,
            description=task.description,
            status=task.status or "pending",
            deadline=task.deadline,
            assigned_to_user_id=task.assigned_to_user_id,
            course_id=task.course_id,
            created_by_id=created_by_id,
            date_created=datetime.utcnow(),
            created_at=datetime.utcnow(),
        )
        self.db.add(task_obj)
        try:
            await self.db.commit()
        except IntegrityError:
            await self.db.rollback()
            raise
        await self.db.refresh(task_obj)
        return self._to_response(task_obj)

    async def update(self, task_id: int, task_data: TaskUpdate) -> Optional[TaskResponse]:
        """Обновить задание"""
        task = await self.db.get(Tasks, task_id)
        if not task:
            return None
        
        update_data = task_data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            if value is not None:
                setattr(task, key, value)
        
        try:
            await self.db.commit()
        except IntegrityError:
            await self.db.rollback()
            raise
        
        await self.db.refresh(task)
        return self._to_response(task)

    async def delete(self, task_id: int) -> bool:
        """Удалить задание"""
        task = await self.db.get(Tasks, task_id)
        if not task:
            return False
        await self.db.delete(task)
        try:
            await self.db.commit()
        except IntegrityError:
            await self.db.rollback()
            raise
        return True

