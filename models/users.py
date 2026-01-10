from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Date
from sqlalchemy.orm import relationship
from core.db import Base

class Users(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    first_name = Column(String(128), nullable=False)
    last_name = Column(String(128), nullable=False)
    middle_name = Column(String, nullable=True)
    email = Column(String(256), nullable=False)
    login = Column(String(50), unique=True, nullable=False)
    birth_date = Column(DateTime, nullable=True)
    is_active = Column(Boolean, nullable=True)

    password_hash = Column(String(256), nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    last_login = Column(DateTime, nullable=True)

    company_id = Column(Integer, ForeignKey("companies.id", ondelete="SET NULL"), nullable=True)
    department_id = Column(Integer, ForeignKey("departments.id", ondelete="SET NULL"), nullable=True)
    position_id = Column(Integer, ForeignKey("positions.id", ondelete="SET NULL"), nullable=True)
    role_id = Column(Integer, ForeignKey("roles.id", ondelete="SET NULL"), nullable=True)

    hire_date = Column(Date, nullable=True)
    telegram_username = Column(String(128), nullable=True, unique=True)

    company = relationship("Company", back_populates="users")
    department = relationship("Department", back_populates="users")
    position = relationship("Position", back_populates="users")
    role = relationship("Role", back_populates="users")

    # tasks
    created_tasks = relationship("Tasks", back_populates="creator", foreign_keys="Tasks.created_by_id")
    assigned_tasks = relationship("Tasks", back_populates="assignee", foreign_keys="Tasks.assigned_to_user_id")

    # groups
    group_links = relationship("GroupsUsers", back_populates="user", cascade="all, delete-orphan")

    # training programs (association object)
    program_links = relationship("TrainingProgramsUsers", back_populates="user", cascade="all, delete-orphan")

    # chat/messages
    messages = relationship("Message", back_populates="user")

    # events
    attendances = relationship("Attendance", back_populates="user")
    trainer_events = relationship("Event", back_populates="trainer", foreign_keys="Event.trainer_id")
    user_answers = relationship("UserAnswer", back_populates="user", cascade="all, delete-orphan")
    
    # course enrollments
    course_enrollments = relationship("CourseEnrollment", back_populates="user", cascade="all, delete-orphan")

