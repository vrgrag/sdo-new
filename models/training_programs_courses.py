from sqlalchemy import Column, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from core.db import Base

class TrainingProgramsCourses(Base):
    __tablename__ = "training_programs_courses"

    id = Column(Integer, primary_key=True)
    create_at = Column(DateTime)

    course_id = Column(Integer, ForeignKey("courses.id"), nullable=True)
    training_program_id = Column(Integer, ForeignKey("programs.id"), nullable=True)

    program = relationship("TrainingProgram", back_populates="course_links")
    course = relationship("Courses", back_populates="program_links")
