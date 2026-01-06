from datetime import datetime
from sqlalchemy import Column, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from core.db import Base

class TrainingProgramsUsers(Base):
    __tablename__ = "training_programs_users"

    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    training_program_id = Column(Integer, ForeignKey("programs.id", ondelete="CASCADE"), nullable=False)

    program = relationship("TrainingProgram", back_populates="user_links")
    user = relationship("Users", back_populates="program_links")
