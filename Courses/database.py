"""
database.py - Конфигурация базы данных и SQLAlchemy модели
Временная заглушка - подключение к БД закомментировано
"""

# from sqlalchemy import create_engine, Column, Integer, String, Text, Float, Boolean, DateTime, ForeignKey, Enum as SQLEnum, JSON, UniqueConstraint, func, BigInteger
# from sqlalchemy.ext.declarative import declarative_base
# from sqlalchemy.orm import sessionmaker, relationship, Session
# from sqlalchemy.dialects.postgresql import UUID
# from enum import Enum
# from datetime import datetime
import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any
from enum import Enum


# --- PostgreSQL ENUM типы (оставляем для типизации) ---
class CourseStatus(str, Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"


class ContentType(str, Enum):
    VIDEO = "video"
    PDF = "pdf"
    DOCX = "docx"
    PPTX = "pptx"
    TEXT = "text"
    IMAGE = "image"


class LessonType(str, Enum):
    THEORY = "theory"
    PRACTICE = "practice"
    TEST = "test"


class UserRole(str, Enum):
    ADMIN = "admin"
    MANAGER = "manager"
    TEACHER = "teacher"
    STUDENT = "student"


"""
# ЗАКОММЕНТИРОВАНО - подключение к реальной БД
# Раскомментировать когда понадобится PostgreSQL

# Конфигурация PostgreSQL
DATABASE_URL = "postgresql://username:password@localhost/courses_db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Создаем PostgreSQL ENUM типы для SQLAlchemy
course_status_enum = SQLEnum(CourseStatus, name="course_status")
content_type_enum = SQLEnum(ContentType, name="content_type")
lesson_type_enum = SQLEnum(LessonType, name="lesson_type")
user_role_enum = SQLEnum(UserRole, name="user_role")

# SQLAlchemy модели для PostgreSQL
class UserDB(Base):
    __tablename__ = "users"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    full_name = Column(String(255), nullable=False)
    role = Column(user_role_enum, default=UserRole.STUDENT)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    is_active = Column(Boolean, default=True)
    avatar_url = Column(String(500), nullable=True)

    created_courses = relationship("CourseDB", back_populates="creator", foreign_keys="[CourseDB.created_by_id]")
    managed_courses = relationship("CourseDB", back_populates="manager", foreign_keys="[CourseDB.assigned_manager_id]")
    enrollments = relationship("EnrollmentDB", back_populates="user")

class CourseDB(Base):
    __tablename__ = "courses"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    title = Column(String(200), nullable=False, index=True)
    description = Column(Text, nullable=False)
    short_description = Column(String(500), nullable=True)
    code = Column(String(50), unique=True, nullable=False, index=True)
    status = Column(course_status_enum, default=CourseStatus.DRAFT)
    image_url = Column(String(500), nullable=True)
    default_image_url = Column(String(500), default="/static/default_course_image.jpg")
    duration_hours = Column(Integer, default=0)

    created_by_id = Column(BigInteger, ForeignKey("users.id"), nullable=False)
    assigned_manager_id = Column(BigInteger, ForeignKey("users.id"), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    tags = Column(JSON, default=[])
    requirements = Column(JSON, default=[])
    what_you_learn = Column(JSON, default=[])

    creator = relationship("UserDB", foreign_keys=[created_by_id], back_populates="created_courses")
    manager = relationship("UserDB", foreign_keys=[assigned_manager_id], back_populates="managed_courses")
    modules = relationship("CourseModuleDB", back_populates="course", cascade="all, delete-orphan")
    enrollments = relationship("EnrollmentDB", back_populates="course")

# Остальные модели аналогично...

# Dependency для получения сессии БД
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Создаем таблицы
Base.metadata.create_all(bind=engine)
"""