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

class TrainingProgramCourse(Base):
    __tablename__ = 'training_programs_courses'
    id = Column(Integer, primary_key=True)
    create_at = Column(DateTime, default=datetime.now)
    course_id = Column(Integer, ForeignKey('courses.id'))
    training_program_id = Column(Integer, ForeignKey('training_programs.id'))