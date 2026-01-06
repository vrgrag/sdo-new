from datetime import datetime

from sqlalchemy import Integer, Column, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from core.db import Base


class Message(Base):
    __tablename__ = "message"

    id = Column(Integer, primary_key=True)
    body = Column(Text, nullable=False)

    attachments_file = Column(Text)  # лучше JSONB
    publication = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    chat_id = Column(Integer, ForeignKey("chat.id", ondelete="CASCADE"), nullable=False)

    user = relationship("Users", back_populates="messages")
    chat = relationship("Chat", back_populates="messages")