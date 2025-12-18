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
    __tablename__ = 'programs'
    id = Column(Integer, primary_key=True)
    title = Column(String(256),nullable=False)
    description = Column(String(256))
    created_by = Column(DateTime, default=datetime.now)
    # organization_id = Column(Integer, ForeignKey("organizations.id"))