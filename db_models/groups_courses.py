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


class GroupsCourses(Base):
    __tablename__ = 'groups_courses'
    id = Column(Integer, primary_key=True)
    group_id = Column(Integer, ForeignKey('groups.id'))
    course_id = Column(Integer, ForeignKey('courses.id'))
    created_at = Column(DateTime, default=datetime.now)