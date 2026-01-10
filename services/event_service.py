# services/event_service.py
from __future__ import annotations

from typing import List

from fastapi import HTTPException
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from models.events import Event
from models.users import Users  # ✅ ВАЖНО: импорт модели пользователя
from models.attendances import Attendance
from repositories.mock.event_repository import EventRepository
from schemas.event import EventCreate, EventUpdate, EventOut


class EventService:
    def __init__(self, db: AsyncSession):
        self.db: AsyncSession = db          # ✅ ВАЖНО: сохраняем db
        self.repo = EventRepository(db)     # репозиторий работает с тем же db

    async def create_event(self, data: EventCreate, current_user: dict) -> Event:
        # trainer_id обязателен (раз ты хочешь привязывать конкретного юзера)
        if data.trainer_id is None:
            raise HTTPException(status_code=400, detail="trainer_id обязателен")

        # Проверяем что такой пользователь существует
        res = await self.db.execute(
            select(Users.id).where(Users.id == data.trainer_id)
        )
        trainer_id = res.scalar_one_or_none()
        if trainer_id is None:
            raise HTTPException(status_code=404, detail="Тренер не найден")

        # (опционально) можно проверить, что это именно trainer по роли:
        # если у Users есть role_id, и ты знаешь id роли trainer
        # или можешь проверить через RoleRepository.

        event = Event(
            title=data.title,
            description=data.description,
            trainer_id=data.trainer_id,
            company_id=data.company_id,
            start_date=data.start_date,
            start_time=data.start_time,
            location=data.location,
            hours_count=data.hours_count,
            seats_count=data.seats_count,
            format=data.format,
        )

        return await self.repo.create(event)

    async def get_event(self, event_id: int) -> Event:
        event = await self.repo.get_by_id(event_id)
        if not event:
            raise HTTPException(status_code=404, detail="Мероприятие не найдено")
        return event

    async def get_event_with_participants(self, event_id: int) -> EventOut:
        """Получить событие с количеством участников"""
        event = await self.get_event(event_id)
        
        # Подсчитываем количество участников
        stmt = select(func.count(Attendance.id)).where(Attendance.event_id == event_id)
        result = await self.db.execute(stmt)
        participants_count = result.scalar() or 0
        
        # Преобразуем Event в EventOut
        event_dict = {
            "id": event.id,
            "title": event.title,
            "description": event.description,
            "trainer_id": event.trainer_id,
            "company_id": event.company_id,
            "start_date": event.start_date,
            "start_time": event.start_time,
            "location": event.location,
            "hours_count": event.hours_count,
            "seats_count": event.seats_count,
            "format": event.format,
            "updated_at": event.updated_at,
            "participants_count": participants_count,
        }
        return EventOut(**event_dict)

    async def list_events(self) -> List[Event]:
        return await self.repo.list_all()

    async def list_events_with_participants(self) -> List[EventOut]:
        """Получить список событий с количеством участников"""
        events = await self.list_events()
        
        # Получаем количество участников для всех событий одним запросом
        event_ids = [e.id for e in events]
        if not event_ids:
            return []
        
        stmt = (
            select(Attendance.event_id, func.count(Attendance.id).label("count"))
            .where(Attendance.event_id.in_(event_ids))
            .group_by(Attendance.event_id)
        )
        result = await self.db.execute(stmt)
        participants_map = {row[0]: row[1] for row in result.all()}
        
        # Формируем ответ
        events_out = []
        for event in events:
            participants_count = participants_map.get(event.id, 0)
            event_dict = {
                "id": event.id,
                "title": event.title,
                "description": event.description,
                "trainer_id": event.trainer_id,
                "company_id": event.company_id,
                "start_date": event.start_date,
                "start_time": event.start_time,
                "location": event.location,
                "hours_count": event.hours_count,
                "seats_count": event.seats_count,
                "format": event.format,
                "updated_at": event.updated_at,
                "participants_count": participants_count,
            }
            events_out.append(EventOut(**event_dict))
        
        return events_out

    async def remove_participant(self, event_id: int, user_id: int) -> None:
        """Удалить участника из события"""
        # Проверяем что событие существует
        event = await self.get_event(event_id)
        
        # Проверяем что запись attendance существует
        stmt = select(Attendance).where(
            Attendance.event_id == event_id,
            Attendance.user_id == user_id
        )
        result = await self.db.execute(stmt)
        attendance = result.scalar_one_or_none()
        
        if not attendance:
            raise HTTPException(status_code=404, detail="Участник не найден в этом мероприятии")
        
        # Удаляем запись
        await self.db.delete(attendance)
        await self.db.commit()

    async def get_participants(self, event_id: int) -> List[dict]:
        """Получить список участников события"""
        # Проверяем что событие существует
        await self.get_event(event_id)
        
        # Получаем участников
        stmt = (
            select(Attendance, Users)
            .join(Users, Users.id == Attendance.user_id)
            .where(Attendance.event_id == event_id)
        )
        result = await self.db.execute(stmt)
        rows = result.all()
        
        participants = []
        for attendance, user in rows:
            participants.append({
                "id": attendance.id,
                "user_id": user.id,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "email": user.email,
                "recorded": attendance.recorded,
                "registered": attendance.registered,
                "invited": attendance.invited,
            })
        
        return participants

    async def update_event(self, event_id: int, data: EventUpdate) -> Event:
        event = await self.get_event(event_id)

        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(event, field, value)

        return await self.repo.update(event)

    async def delete_event(self, event_id: int) -> None:
        event = await self.get_event(event_id)
        await self.repo.delete(event)
