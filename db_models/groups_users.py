from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from db.base import Base

class GroupsUsers(Base):
    __tablename__ = "groups_users"

    id = Column(Integer, primary_key=True)
    group_id = Column(Integer, ForeignKey("groups.id"), nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    group = relationship("Groups", back_populates="user_links")
    user = relationship("Users", back_populates="group_links")
