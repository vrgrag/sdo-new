from datetime import datetime
from sqlalchemy import (
Column,
Integer,
String,
Text,
DateTime,
ForeignKey
)
from sqlalchemy.orm import relationship
from core.db import Base


class Tasks(Base):
    __tablename__ = 'tasks'
    id = Column(Integer, primary_key=True)
    title = Column(String(256),nullable=False)
    description = Column(String(256))
    status = Column(String)
    date_created = Column(DateTime, default=datetime.now)
    deadline = Column(DateTime)
    assigned_to_user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    created_at = Column(DateTime, default=datetime.now)
    created_by_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    course_id = Column(Integer, ForeignKey("courses.id", ondelete="CASCADE"), nullable=False)

    course = relationship("Courses", back_populates="tasks")
    assignee = relationship("Users", back_populates="assigned_tasks", foreign_keys=[assigned_to_user_id])
    creator = relationship("Users", back_populates="created_tasks", foreign_keys=[created_by_id])
