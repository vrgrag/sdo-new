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


class Materials(Base):
    __tablename__ = 'materials'
    id = Column(Integer, primary_key=True)
    title = Column(Text, nullable=False)
    number_of_pages = Column(Integer, nullable=False)
    description = Column(Text, nullable=False)
    file_path = Column(Text, nullable=False)
