from datetime import datetime
from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DateTime,
    ForeignKey, Boolean, NVARCHAR
)
from sqlalchemy.orm import relationship
from db.base import Base


class Users(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    first_name = Column(String(128), nullable=False)
    last_name = Column(String(128), nullable=False)
    middle_name = Column(String)
    email = Column(String(256), nullable=False)
    birth_date = Column(DateTime)
    is_active = Column(Boolean)
    password_hash = Column(String(256), nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    last_login = Column(DateTime)
    company_id = Column(Integer, ForeignKey('companies.id'))
    department_id = Column(Integer, ForeignKey('departments.id'))
    position_id = Column(Integer, ForeignKey('positions.id'))
    role_id = Column(Integer, ForeignKey('roles.id'))
    training_programs = relationship(
        "TrainingPrograms",
        secondary="training_programs_users",
        back_populates="users"
    )
    company_id = Column(Integer, ForeignKey("companies.id", ondelete="SET NULL"))
    department_id = Column(Integer, ForeignKey("department.id", ondelete="SET NULL"))
    position_id = Column(Integer, ForeignKey("positions.id", ondelete="SET NULL"))
    role_id = Column(Integer, ForeignKey("roles.id", ondelete="SET NULL"))

    department = relationship("Department", back_populates="users")
    position = relationship("Position", back_populates="users")
    role = relationship("Role", back_populates="users")

    # tasks
    created_tasks = relationship("Task", back_populates="creator", foreign_keys="Task.created_by_id")
    assigned_tasks = relationship("Task", back_populates="assignee", foreign_keys="Task.assigned_to_user_id")

    # groups/programs
    group_links = relationship("GroupUser", back_populates="user", cascade="all, delete-orphan")
    program_links = relationship("TrainProgramUser", back_populates="user", cascade="all, delete-orphan")

    # chat/messages
    messages = relationship("Message", back_populates="user")

    # events
    attendances = relationship("Attendance", back_populates="user")
    trainer_events = relationship("Event", back_populates="trainer", foreign_keys="Event.trainer_id")
