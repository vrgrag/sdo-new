from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from core.db import Base


class Position(Base):
    __tablename__ = 'positions'
    id = Column(Integer, primary_key=True)
    name = Column(String(256), nullable=False)

    users = relationship("Users", back_populates="position")
    department_links = relationship("DepartmentPosition", back_populates="position", cascade="all, delete-orphan")
    departments = relationship("Department", secondary="department_positions", viewonly=True)