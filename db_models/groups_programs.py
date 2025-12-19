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

from db.base import Base


class GroupProgram(Base):
    __tablename__ = "groups_program"

    id = Column(Integer, primary_key=True)
    groups_id = Column(Integer, ForeignKey("groups.id", ondelete="CASCADE"), nullable=False)
    program_id = Column(Integer, ForeignKey("training_programs.id", ondelete="CASCADE"), nullable=False)

    group = relationship("Group", back_populates="program_links")
    program = relationship("TrainingProgram", back_populates="group_links")

