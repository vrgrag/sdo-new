from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship

from db.base import Base


class CourseCompany(Base):
    __tablename__ = "courses_companies"

    id = Column(Integer, primary_key=True)
    course_id = Column(Integer, ForeignKey("courses.id"))
    company_id = Column(Integer, ForeignKey("companies.id"))
    course = relationship("Course", back_populates="courses")
    company = relationship("Company", back_populates="courses")