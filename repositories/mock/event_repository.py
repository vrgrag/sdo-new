# repositories/mock_event_repository.py
import datetime
import json
import os
from typing import List, Optional
from schemas.event import EventResponse, EventCreate

DATA_FILE = "db/events.json"  # теперь в папке db, как ты любишь
os.makedirs("db", exist_ok=True)

class MockEventRepository:
    def __init__(self):
        self._load()

    def _load(self):
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.events = [EventResponse(**e) for e in data]
        else:
            self.events = []

    def _save(self):
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump([e.dict() for e in self.events], f, ensure_ascii=False, indent=2, default=str)

    def create(self, event_data: EventCreate) -> EventResponse:
        new_id = (max([e.id for e in self.events], default=0) + 1)
        from datetime import datetime
        now = datetime.utcnow()
        event = EventResponse(
            **event_data.dict(),
            id=new_id,
            registered_count=0,
            created_at=now,
            updated_at=now
        )
        self.events.append(event)
        self._save()
        return event

    def get_all(self) -> List[EventResponse]:
        return self.events

    def get_by_id(self, event_id: int) -> Optional[EventResponse]:
        for e in self.events:
            if e.id == event_id:
                return e
        return None

    def update(self, event_id: int, event_data: EventCreate) -> Optional[EventResponse]:
        for i, event in enumerate(self.events):
            if event.id == event_id:
                from datetime import datetime
                now = datetime.utcnow()
                updated_event = EventResponse(
                    **event_data.dict(),
                    id=event_id,
                    registered_count=event.registered_count,
                    created_at=event.created_at,
                    updated_at=now
                )
                self.events[i] = updated_event
                self._save()
                return updated_event
        return None

    def delete(self, event_id: int) -> bool:
        for i, event in enumerate(self.events):
            if event.id == event_id:
                self.events.pop(i)
                self._save()
                return True
        return False
