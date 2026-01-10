from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from core.db import Base

class TrainingProgram(Base):
    __tablename__ = "programs"

    id = Column(Integer, primary_key=True)
    title = Column(String(256), nullable=False)
    description = Column(String(256))
    created_by = Column(DateTime, default=datetime.utcnow)
    company_id = Column(Integer, ForeignKey("companies.id",  ondelete="CASCADE"), nullable=True)

    company = relationship("Company", back_populates="programs")

    user_links = relationship("TrainingProgramsUsers", back_populates="program", cascade="all, delete-orphan")
    course_links = relationship("TrainingProgramsCourses", back_populates="program", cascade="all, delete-orphan")
    group_links = relationship("GroupProgram", back_populates="program", cascade="all, delete-orphan")

