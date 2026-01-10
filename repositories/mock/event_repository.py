# repositories/event_repository.py
from __future__ import annotations

from typing import Optional, List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.events import Event


class EventRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, event: Event) -> Event:
        self.db.add(event)
        await self.db.commit()
        await self.db.refresh(event)
        return event

    async def get_by_id(self, event_id: int) -> Optional[Event]:
        q = select(Event).where(Event.id == event_id)
        res = await self.db.execute(q)
        return res.scalar_one_or_none()

    async def list_all(self) -> List[Event]:
        q = select(Event).order_by(Event.start_date.desc(), Event.start_time.desc())
        res = await self.db.execute(q)
        return list(res.scalars().all())

    async def update(self, event: Event) -> Event:
        # event уже изменён снаружи
        await self.db.commit()
        await self.db.refresh(event)
        return event

    async def delete(self, event: Event) -> None:
        await self.db.delete(event)
        await self.db.commit()
