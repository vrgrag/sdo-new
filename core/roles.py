# core/roles.py
from enum import Enum

class UserRole(str, Enum):
    ADMIN = "admin"
    MANAGER = "manager"
    TRAINER = "trainer"
    STUDENT = "student"
