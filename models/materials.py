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

from core.db import Base


class Materials(Base):
    __tablename__ = 'materials'
    id = Column(Integer, primary_key=True)
    title = Column(String(256), nullable=False)
    number_of_pages = Column(Integer)
    description = Column(Text, nullable=False)
    file_path = Column(String(256), nullable=False)

    course_id = Column(Integer, ForeignKey("courses.id", ondelete="CASCADE"), nullable=False)
    course = relationship("Courses", back_populates="materials")
