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


class Tests(Base):
    __tablename__ = 'tests'
    id = Column(Integer, primary_key=True)
    title = Column(String)
    description = Column(String)
    number_of_attempts = Column(Integer)
    created_at = Column(DateTime, default=datetime.now)
    time_limit_minutes = Column(Integer)