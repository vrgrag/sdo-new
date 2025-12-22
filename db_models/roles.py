from sqlalchemy import Column, String, Integer
from sqlalchemy.orm import relationship

from db.base import Base

class Role(Base):
    __tablename__ = 'roles'
    id = Column(Integer, primary_key=True)
    title = Column(String(256), nullable=False)
    users = relationship("Users", back_populates="role")