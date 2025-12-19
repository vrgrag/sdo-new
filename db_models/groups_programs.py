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


class TrainingPrograms(Base):
    __tablename__ = 'training_programs_users'

    id = Column(Integer, primary_key=True)
    group_id = Column(Integer, ForeignKey('groups.id'))
    program_id = Column(Integer, ForeignKey('programs.id'))

    group = relationship("Group", back_populates="program_links")
    program = relationship("TrainingProgram", back_populates="group_links")
