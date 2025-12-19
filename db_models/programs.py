from datetime import datetime
from sqlalchemy import (
Column,
Integer,
String,
Text,
DateTime,
ForeignKey
)
from sqlalchemy.orm import relationship
from db.base import Base


class TrainingPrograms(Base):
    __tablename__ = 'training_programs'
    id = Column(Integer, primary_key=True)
    title = Column(String(256),nullable=False)
    description = Column(String(256))
    created_by = Column(DateTime, default=datetime.now)
    company_id = Column(Integer, ForeignKey("companies.id"))

    company = relationship("Company", back_populates="programs")
    user_links = relationship("TrainProgramUser", back_populates="program", cascade="all, delete-orphan")
    course_links = relationship("TrainProgramCourse", back_populates="program", cascade="all, delete-orphan")
    group_links = relationship("GroupProgram", back_populates="program", cascade="all, delete-orphan")
