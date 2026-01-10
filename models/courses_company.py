from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from core.db import Base

class CourseCompany(Base):
    __tablename__ = "courses_companies"

    id = Column(Integer, primary_key=True)
    course_id = Column(Integer, ForeignKey("courses.id", ondelete="CASCADE"), nullable=False)
    company_id = Column(Integer, ForeignKey("companies.id",  ondelete="CASCADE"), nullable=False)

    course = relationship("Courses", back_populates="companies_links")
    company = relationship("Company", back_populates="course_links")
