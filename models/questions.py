from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from core.db import Base


class Question(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True)
    test_id = Column(Integer, ForeignKey("tests.id"))
    question_text = Column(String)
    question_type = Column(String)

    test = relationship("Tests", back_populates="questions")
    answers = relationship("Answer", back_populates="question", cascade="all, delete-orphan")
    user_answers = relationship("UserAnswer", back_populates="question", cascade="all, delete-orphan")
