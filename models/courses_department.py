from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from core.db import Base

class CourseDepartment(Base):
    __tablename__ = "courses_department"

    id = Column(Integer, primary_key=True)
    course_id = Column(Integer, ForeignKey("courses.id",  ondelete="CASCADE"), nullable=False)
    department_id = Column(Integer, ForeignKey("departments.id",  ondelete="CASCADE"), nullable=False)

    course = relationship("Courses", back_populates="departments_links")
    department = relationship("Department", back_populates="courses_links")
