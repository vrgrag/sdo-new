from datetime import datetime
from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey,
    UniqueConstraint
)
from sqlalchemy.orm import relationship
from core.db import Base


class CourseEnrollment(Base):
    __tablename__ = "course_enrollments"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    course_id = Column(Integer, ForeignKey("courses.id", ondelete="CASCADE"), nullable=False)
    enrollment_type = Column(String(20), nullable=False)  # 'student' или 'trainer'
    enrolled_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    
    # Уникальность: один пользователь не может быть записан дважды на один курс с одним типом
    __table_args__ = (
        UniqueConstraint('user_id', 'course_id', 'enrollment_type', name='uq_user_course_type'),
    )
    
    user = relationship("Users", back_populates="course_enrollments")
    course = relationship("Courses", back_populates="enrollments")


