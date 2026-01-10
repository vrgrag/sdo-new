from datetime import datetime
from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DateTime,
    ForeignKey,
    Boolean
)
from sqlalchemy.orm import relationship
from core.db import Base


class Lessons(Base):
    __tablename__ = "lessons"
    
    id = Column(Integer, primary_key=True)
    course_id = Column(Integer, ForeignKey("courses.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(256), nullable=False)
    
    content_type = Column(String(50), nullable=False)  # video, pdf, docx, pptx, text, image
    content_url = Column(String(512), nullable=True)
    content_text = Column(Text, nullable=True)
    
    duration_minutes = Column(Integer, default=0, nullable=False)
    order = Column(Integer, default=0, nullable=False)
    lesson_type = Column(String(50), default="theory", nullable=False)  # theory, practice, test
    is_published = Column(Boolean, default=True, nullable=False)
    
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), nullable=True, onupdate=datetime.utcnow)
    
    course = relationship("Courses", back_populates="lessons")

