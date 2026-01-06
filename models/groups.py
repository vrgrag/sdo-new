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
class Groups(Base):
    __tablename__ = 'groups'

    id = Column(Integer, primary_key=True)
    name = Column(String(256),nullable=False)
    description = Column(String(256))
    users_id = Column(Integer, ForeignKey('users.id'))
    deadline = Column(DateTime)
    course_id = Column(Integer, ForeignKey('courses.id'))
    create_at = Column(DateTime)
    passage_programs = Column(Boolean)

    user_links = relationship("GroupsUsers", back_populates="group", cascade="all, delete-orphan")
    course_links = relationship("GroupsCourses", back_populates="group", cascade="all, delete-orphan")
    program_links = relationship("GroupProgram", back_populates="group", cascade="all, delete-orphan")
