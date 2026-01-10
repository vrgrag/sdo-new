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


class GroupsCourses(Base):
    __tablename__ = 'groups_courses'
    id = Column(Integer, primary_key=True)
    group_id = Column(Integer, ForeignKey('groups.id',  ondelete="CASCADE"))
    course_id = Column(Integer, ForeignKey('courses.id',  ondelete="CASCADE"),nullable=True)
    created_at = Column(DateTime)

    group = relationship("Groups", back_populates="course_links")
    course = relationship("Courses", back_populates="group_links")
