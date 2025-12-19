from datetime import datetime

from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime

from db.base import Base


class Event(Base):
    __tablename__ = "event"

    id = Column(Integer, primary_key=True)
    title = Column(String(100), nullable=False)
    description = Column(Text)

    trainer_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    event_date = Column(DateTime(timezone=True))

    format_event = Column(String(50))
    updated_date = Column(DateTime(timezone=True), onupdate=datetime.utcnow)
    create_date = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    trainer = relationship("User", back_populates="trainer_events", foreign_keys=[trainer_id])
    attendances = relationship("Attendance", back_populates="event", cascade="all, delete-orphan")


