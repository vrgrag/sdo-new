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

class TrainingProgramsUsers(Base):
    __tablename__ = 'training_programs_users'
id = Column(Integer, primary_key=True)
create_at = Column(DateTime, default=datetime.now)
user_id = Column(Integer, ForeignKey('users.id'))
training_program_id = Column(Integer, ForeignKey('training_programs.id'))