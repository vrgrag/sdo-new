# 📁 repositories/base.py
from abc import ABC, abstractmethod
from typing import List, Optional, Dict

from schemas import CourseResponse, CourseCreate, CourseUpdate, CourseStatus
from schemas import LessonResponse



class ICourseRepository(ABC):


    @abstractmethod
    def get_all(
        self,
        status: Optional[CourseStatus] = None,
        limit: int = 20,
        offset: int = 0,
        search: Optional[str] = None
    ) -> List[CourseResponse]:

        pass

    @abstractmethod
    def get_by_id(self, course_id: int) -> Optional[CourseResponse]:

        pass

    @abstractmethod
    def create(self, course_data: CourseCreate) -> CourseResponse:
        pass

    @abstractmethod
    def update(self, course_id: int, course_data: CourseUpdate) -> Optional[CourseResponse]:
        pass

    @abstractmethod
    def delete(self, course_id: int) -> bool:

        pass
class ILessonRepository(ABC):  # ← этот класс должен быть здесь
    @abstractmethod
    def get_all(
        self,
        module_id: Optional[int] = None,
        lesson_type: Optional[str] = None
    ) -> List[LessonResponse]:
        pass

    @abstractmethod
    def get_by_id(self, lesson_id: int) -> Optional[LessonResponse]:
        pass


class IModuleRepository(ABC):
    @abstractmethod
    def get_by_course(self, course_id: int) -> List[Dict]:
        pass

    @abstractmethod
    def get_by_id(self, module_id: int) -> Optional[Dict]:
        pass

__all__ = ["ICourseRepository", "ILessonRepository"]