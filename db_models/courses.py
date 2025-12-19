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


class Courses(Base):
    __tablename__ = "courses"
    id = Column(Integer, primary_key=True)

    title = Column(String(100), nullable=False)
    description = Column(Text)

    status = Column(Boolean, default=False, nullable=False)  # draft/published
    image = Column(String)

    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=datetime.utcnow)
    deadline = Column(DateTime(timezone=True))


    tests = relationship("Tests", back_populates="courses")
    materials = relationship("Materials", back_populates="courses")
    group_links = relationship("GroupCourse", back_populates="course", cascade="all, delete-orphan")
    companies_links = relationship("CourseCompany", back_populates="course", cascade="all, delete-orphan")
    departments_links = relationship("CourseDepartment", back_populates="course", cascade="all, delete-orphan")
    program_links = relationship("TrainProgramCourse", back_populates="course", cascade="all, delete-orphan")
