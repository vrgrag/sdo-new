from datetime import datetime
from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DateTime,
    ForeignKey, Boolean
)
from sqlalchemy.orm import relationship
from db.base import Base


class Users(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    first_name = Column(String)
    last_name = Column(String)
    middle_name = Column(String)
    email = Column(String)
    birth_date = Column(DateTime)
    is_active = Column(Boolean)
    password = Column(String)
    created_at = Column(DateTime)
    last_login = Column(DateTime)
    company_id = Column(Integer, ForeignKey('companies.id'))
    department_id = Column(Integer, ForeignKey('departments.id'))
    position_id = Column(Integer, ForeignKey('positions.id'))
    role_id = Column(Integer, ForeignKey('roles.id'))