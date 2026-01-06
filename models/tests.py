from datetime import datetime
from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DateTime,
    ForeignKey, Boolean
)
from sqlalchemy.orm import relationship

from core.db import Base


class Tests(Base):
    __tablename__ = 'tests'
    id = Column(Integer, primary_key=True)
    title = Column(String(256),nullable=False)
    description = Column(String(256))
    number_of_attempts = Column(Integer)
    created_at = Column(DateTime)
    time_limit_minutes = Column(Integer)
    course_id = Column(Integer, ForeignKey('courses.id'),nullable=True)

    course = relationship("Courses", back_populates="tests")
    questions = relationship("Question", back_populates="test", cascade="all, delete-orphan")
