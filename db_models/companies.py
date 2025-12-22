from datetime import datetime

from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from db.base import Base


class Company(Base):
    __tablename__ = 'companies'
    id = Column(Integer, primary_key=True)
    name = Column(String(256), nullable=False)
    departments = relationship("Department", back_populates="company", cascade="all, delete-orphan")
    course_links = relationship("CourseCompany", back_populates="company", cascade="all, delete-orphan")
    programs = relationship("TrainingProgram", back_populates="company", cascade="all, delete-orphan")
    users = relationship("Users", back_populates="company")

    