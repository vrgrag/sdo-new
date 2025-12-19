import enum
from sqlalchemy import Column, Integer, Text, Enum
from sqlalchemy.orm import relationship

from db.base import Base


class ChatStatus(str, enum.Enum):
    active = "active"
    archive = "archive"


class Chat(Base):
    __tablename__ = "chat"

    id = Column(Integer, primary_key=True)
    title = Column(Text, nullable=False)
    status = Column(Enum(ChatStatus, name="chat_status"), default=ChatStatus.active, nullable=False)

    messages = relationship("Message", back_populates="chat", cascade="all, delete-orphan")

