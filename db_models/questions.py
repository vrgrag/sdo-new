from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from db.base import Base


class Question(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True)
    test_id = Column(Integer, ForeignKey("tests.id"))
    question_text = Column(String)
    question_type = Column(String)

    test = relationship("Test", back_populates="questions")
    answer = relationship("Answer", back_populates="questions")
    user_answer = relationship("UserAnswer", back_populates="questions")