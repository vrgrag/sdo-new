# repositories/__init__.py

from .base import ICourseRepository, ILessonRepository

from .mock.course_repository import JsonCourseRepository
from .mock.lesson_repository import JsonLessonRepository
from .mock.user_repository import  UserRepository
from .mock.enrollment_repository import EnrollmentRepository

__all__ = [
    "ICourseRepository",
    "ILessonRepository",
    "JsonCourseRepository",
    "JsonLessonRepository",
    "UserRepository",
    "EnrollmentRepository",
]
