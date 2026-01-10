# schemas/event.py
from pydantic import BaseModel
from typing import Optional, Literal
from datetime import date, time, datetime


EventFormat = Literal["offline", "online", "hybrid"]


class EventBase(BaseModel):
    title: str
    description: Optional[str] = None

    trainer_id: Optional[int] = None
    company_id: int

    start_date: date
    start_time: time

    location: Optional[str] = None
    hours_count: Optional[int] = None
    seats_count: Optional[int] = None
    format: Optional[EventFormat] = None


class EventCreate(EventBase):
    pass


class EventUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None

    trainer_id: Optional[int] = None
    company_id: Optional[int] = None

    start_date: Optional[date] = None
    start_time: Optional[time] = None

    location: Optional[str] = None
    hours_count: Optional[int] = None
    seats_count: Optional[int] = None
    format: Optional[EventFormat] = None


class EventOut(EventBase):
    id: int
    updated_at: datetime
    participants_count: int = 0  # Количество участников

    class Config:
        from_attributes = True
