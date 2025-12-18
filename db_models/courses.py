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


class Courses(Base):
    __tablename__ = "courses"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(256), nullable=False)
    description = Column(String(100), nullable=False)
    created_by_user_id = Column(Integer, ForeignKey("user.id"))
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    deadline = Column(DateTime, nullable=True)

