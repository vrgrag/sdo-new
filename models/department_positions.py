from sqlalchemy import Column, Integer, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship

from core.db import Base


class DepartmentPosition(Base):
    __tablename__ = "department_positions"

    id = Column(Integer, primary_key=True)
    position_id = Column(Integer, ForeignKey("positions.id", ondelete="CASCADE"), nullable=False)
    department_id = Column(Integer, ForeignKey("departments.id", ondelete="CASCADE"), nullable=False)

    __table_args__ = (
        UniqueConstraint("position_id", "department_id", name="uq_department_positions_position_department"),
    )

    position = relationship("Position", back_populates="department_links")
    department = relationship("Department", back_populates="position_links")
