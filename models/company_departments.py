from sqlalchemy import Column, Integer, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship

from core.db import Base


class CompanyDepartment(Base):
    __tablename__ = "company_departments"

    id = Column(Integer, primary_key=True)
    company_id = Column(Integer, ForeignKey("companies.id", ondelete="CASCADE"), nullable=False)
    department_id = Column(Integer, ForeignKey("departments.id", ondelete="CASCADE"), nullable=False)

    __table_args__ = (
        UniqueConstraint("company_id", "department_id", name="uq_company_departments_company_department"),
    )

    company = relationship("Company", back_populates="department_links")
    department = relationship("Department", back_populates="company_links")
