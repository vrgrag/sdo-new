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
from db.base import Base
class Groups(Base):
    __tablename__ = 'groups'

    id = Column(Integer, primary_key=True)
    name = Column(String(256),nullable=False)
    description = Column(String(256))
    users_id = Column(Integer, ForeignKey('users.id'))
    dedline = Column(DateTime)
    course_id = Column(Integer, ForeignKey('courses.id'))
    create_at = Column(DateTime)
    passage_programs = Column(Boolean)