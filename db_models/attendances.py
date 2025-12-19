from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship

from db.base import Base


class Attendance(Base):
    __tablename__ = "attendance"

    id = Column(Integer, primary_key=True)

    recorded = Column(Integer)
    registered = Column(Integer)
    invited = Column(Integer)

    event_id = Column(Integer, ForeignKey("event.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    event = relationship("Event", back_populates="attendances")
    user = relationship("User", back_populates="attendances")