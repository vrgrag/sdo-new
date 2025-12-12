# repositories/__init__.py

from .base import ICourseRepository, ILessonRepository, IModuleRepository

from .mock.course_repository import JsonCourseRepository
from .mock.module_repository import JsonModuleRepository
from .mock.lesson_repository import JsonLessonRepository
from .mock.user_repository import user_repository, UserRepository
from .mock.enrollment_repository import EnrollmentRepository

__all__ = [
    "ICourseRepository",
    "ILessonRepository",
    "IModuleRepository",
    "JsonCourseRepository",
    "JsonModuleRepository",
    "JsonLessonRepository",
    "UserRepository",
    "user_repository",
    "EnrollmentRepository",
]
