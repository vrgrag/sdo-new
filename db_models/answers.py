from sqlalchemy import Column, Integer, String, ForeignKey, Boolean
from sqlalchemy.orm import relationship
class Answer(Base):
    __tablename__ = "answers"
    id = Column(Integer, primary_key=True)
    question_id = Column(Integer, ForeignKey("questions.id"))
    question_text = Column(String)
    is_correct = Column(Boolean)
    question = relationship("Question", back_populates="answers")
    selected_in = relationship("UserAnswer", back_populates="selected_answer")
