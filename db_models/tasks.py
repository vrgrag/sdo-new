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


class Tasks(Base):
    __tablename__ = 'tasks'
    id = Column(Integer, primary_key=True)
    title = Column(String(256),nullable=False)
    description = Column(String(256))
    status = Column(String)
    date_created = Column(DateTime, default=datetime.now)
    deadline = Column(DateTime)
    asigened_to_user_id = Column(Integer, ForeignKey('users.id'))
    created_at = Column(DateTime, default=datetime.now)
    created_by = relationship('Users', foreign_keys=[asigened_to_user_id])