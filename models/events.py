# models/events.py
from sqlalchemy import (
    Column, Integer, String, Text, Date, Time, DateTime, ForeignKey, func
)
from sqlalchemy.orm import relationship

from core.db import Base


class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)

    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)

    trainer_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    start_date = Column(Date, nullable=False)
    start_time = Column(Time, nullable=False)

    location = Column(String(255), nullable=True)
    hours_count = Column(Integer, nullable=True)
    seats_count = Column(Integer, nullable=True)
    format = Column(String(50), nullable=True)

    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    company_id = Column(Integer, ForeignKey("companies.id", ondelete="CASCADE"), nullable=False)

    trainer = relationship("Users", back_populates="events_as_trainer")
    company = relationship("Company", back_populates="events")
