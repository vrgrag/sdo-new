from datetime import datetime
from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DateTime,
    ForeignKey, Boolean, JSON
)
from sqlalchemy.orm import relationship
from core.db import Base


class Courses(Base):
    __tablename__ = "courses"
    id = Column(Integer, primary_key=True)

    title = Column(String(100), nullable=False)
    description = Column(Text)
    short_description = Column(Text, nullable=True)
    
    status = Column(String(20), default="draft", nullable=False)  # draft/published/archived
    image = Column(String, nullable=True)  # путь к изображению
    
    duration_hours = Column(Integer, default=0, nullable=False)
    
    # JSON поля для списков
    tags = Column(JSON, default=list, nullable=True)
    requirements = Column(JSON, default=list, nullable=True)
    what_you_learn = Column(JSON, default=list, nullable=True)

    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), nullable=True, onupdate=datetime.utcnow)
    deadline = Column(DateTime(timezone=True), nullable=True)

    tests = relationship("Tests", back_populates="course", cascade="all, delete-orphan")
    lessons = relationship("Lessons", back_populates="course", cascade="all, delete-orphan")
    materials = relationship("Materials", back_populates="course", cascade="all, delete-orphan")

    group_links = relationship("GroupsCourses", back_populates="course", cascade="all, delete-orphan")
    companies_links = relationship("CourseCompany", back_populates="course", cascade="all, delete-orphan")
    departments_links = relationship("CourseDepartment", back_populates="course", cascade="all, delete-orphan")
    program_links = relationship("TrainingProgramsCourses", back_populates="course", cascade="all, delete-orphan")
    tasks = relationship("Tasks", back_populates="course", cascade="all, delete-orphan")
    enrollments = relationship("CourseEnrollment", back_populates="course", cascade="all, delete-orphan")