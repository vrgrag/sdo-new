# services/event_service.py
from repositories.mock.event_repository import MockEventRepository
from schemas.event import EventCreate, EventResponse
from typing import List
from fastapi import HTTPException, status
class EventService:
    def __init__(self, event_repo: MockEventRepository):
        self.event_repo = event_repo

    def create_event(self, event_data: EventCreate) -> EventResponse:
        return self.event_repo.create(event_data)

    def get_all_events(self) -> List[EventResponse]:
        return self.event_repo.get_all()

    def get_event(self, event_id: int) -> EventResponse:
        event = self.event_repo.get_by_id(event_id)
        if not event:
            raise ValueError("Мероприятие не найдено")
        return event

    def update_event(self, event_id: int, event_data: EventCreate) -> EventResponse:
        event = self.event_repo.update(event_id, event_data)
        if not event:
            raise HTTPException(status_code=404, detail="Мероприятие не найдено")
        return event

    def delete_event(self, event_id: int):
        success = self.event_repo.delete(event_id)
        if not success:
            raise HTTPException(status_code=404, detail="Мероприятие не найдено")