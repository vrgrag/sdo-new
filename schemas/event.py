# schemas/event.py
from pydantic import BaseModel
from typing import List, Literal, Optional
from datetime import datetime

class EventCriteriaSchema(BaseModel):
    name: str
    type: Literal["range", "text", "static"]
    min_value: Optional[int] = None
    max_value: Optional[int] = None
    step: Optional[int] = 1
    static_options: Optional[str] = None

    class Config:
        from_attributes = True

class EventCreate(BaseModel):
    title: str
    description: Optional[str] = None
    date: datetime
    duration_minutes: int
    format: Literal["offline", "online", "hybrid"]
    max_seats: int
    trainer_ids: List[int] = []
    invited_student_ids: List[int] = []
    criteria: List[EventCriteriaSchema] = []

class EventResponse(EventCreate):
    id: int
    registered_count: int = 0
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True