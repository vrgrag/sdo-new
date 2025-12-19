from datetime import datetime

from sqlalchemy import Column, Integer, ForeignKey, Boolean, DateTime
from sqlalchemy.orm import relationship

from db.base import Base


class UserAnswer(Base):
    __tablename__ = "user_answer"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    question_id = Column(Integer, ForeignKey("questions.id", ondelete="CASCADE"), nullable=False)
    selected_answer_id = Column(Integer, ForeignKey("answer.id", ondelete="SET NULL"))

    is_correct = Column(Boolean, default=False, nullable=False)
    answered_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    user = relationship("User")
    question = relationship("Question", back_populates="user_answers")
    selected_answer = relationship("Answer", back_populates="selected_in")
