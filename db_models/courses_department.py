from sqlalchemy import Column, DateTime, Integer, ForeignKey
from sqlalchemy.orm import relationship

from db.base import Base


class CourseDepartment(Base):
    __tablename__ = "courses_department"
    id = Column(Integer, primary_key=True, autoincrement=True)
    course_id = Column(Integer, ForeignKey("courses.id"))
    department_id = Column(Integer, ForeignKey("departments.id"))

    course = relationship("Course", back_populates="department")
    department = relationship("Department", back_populates="course")