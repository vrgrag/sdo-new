# from datetime import datetime
# from sqlalchemy import (
# Column,
# Integer,
# String,
# Text,
# DateTime,
# ForeignKey
# )
# from sqlalchemy.orm import relationship
# from db.base import Base
#
#
# class Modules(Base):
#     __tablename__ = 'modules'
#     id = Column(Integer, primary_key=True)
#     course_id = Column(Integer, ForeignKey('courses.id'))
#     material_id = Column(Integer, ForeignKey('materials.id'))
