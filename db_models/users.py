from datetime import datetime
from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DateTime,
    ForeignKey, Boolean, NVARCHAR
)
from sqlalchemy.orm import relationship
from db.base import Base


class Users(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    first_name = Column(String(128), nullable=False)
    last_name = Column(String(128), nullable=False)
    middle_name = Column(String)
    email = Column(String(256), nullable=False)
    birth_date = Column(DateTime)
    is_active = Column(Boolean)
    password_hash = Column(String(256), nullable=False)
    created_at = Column(DateTime)
    last_login = Column(DateTime)
    company_id = Column(Integer, ForeignKey('companies.id'))
    department_id = Column(Integer, ForeignKey('departments.id'))
    position_id = Column(Integer, ForeignKey('positions.id'))
    role_id = Column(Integer, ForeignKey('roles.id'))