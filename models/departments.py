from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from core.db import Base


class Department(Base):
    __tablename__ = 'departments'
    id = Column(Integer, primary_key=True)
    name = Column(String(256), nullable=False)
    company_id = Column(Integer, ForeignKey('companies.id', ondelete="CASCADE"), nullable=False)
    company_links = relationship("CompanyDepartment", back_populates="department", cascade="all, delete-orphan")
    company = relationship("Company", back_populates="departments")
    users = relationship("Users", back_populates="department")
    courses_links = relationship("CourseDepartment", back_populates="department", cascade="all, delete-orphan")
    position_links = relationship("DepartmentPosition", back_populates="department", cascade="all, delete-orphan")
    positions = relationship("Position", secondary="department_positions", viewonly=True)
