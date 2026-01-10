# 📁 repositories/base.py
from abc import ABC, abstractmethod
from typing import List, Optional, Dict

from schemas import CourseResponse, CourseCreate, CourseUpdate, CourseStatus
from schemas import LessonResponse, LessonCreate, LessonUpdate
from schemas import ModuleResponse, ModuleCreate, ModuleUpdate



class ICourseRepository(ABC):

    @abstractmethod
    async def get_all(
        self,
        status: Optional[CourseStatus] = None,
        limit: int = 20,
        offset: int = 0,
        search: Optional[str] = None
    ) -> List[CourseResponse]:
        pass

    @abstractmethod
    async def get_by_id(self, course_id: int) -> Optional[CourseResponse]:
        pass

    @abstractmethod
    async def create(self, course_data: CourseCreate) -> CourseResponse:
        pass

    @abstractmethod
    async def update(self, course_id: int, course_data: CourseUpdate) -> Optional[CourseResponse]:
        pass

    @abstractmethod
    async def delete(self, course_id: int) -> bool:
        pass
class ILessonRepository(ABC):
    @abstractmethod
    async def get_all(
        self,
        course_id: Optional[int] = None,
        lesson_type: Optional[str] = None
    ) -> List[LessonResponse]:
        pass

    @abstractmethod
    async def get_by_id(self, lesson_id: int) -> Optional[LessonResponse]:
        pass

    @abstractmethod
    async def get_by_course(self, course_id: int) -> List[LessonResponse]:
        pass

    @abstractmethod
    async def create(self, lesson: LessonCreate) -> LessonResponse:
        pass

    @abstractmethod
    async def update(
        self,
        lesson_id: int,
        lesson_data: LessonUpdate
    ) -> Optional[LessonResponse]:
        pass

    @abstractmethod
    async def delete(self, lesson_id: int) -> bool:
        pass


class IModuleRepository(ABC):
    @abstractmethod
    async def get_by_course(self, course_id: int) -> List[ModuleResponse]:
        pass

    @abstractmethod
    async def get_by_id(self, module_id: int) -> Optional[ModuleResponse]:
        pass

    @abstractmethod
    async def create(self, module_data: ModuleCreate) -> ModuleResponse:
        pass

    @abstractmethod
    async def update(self, module_id: int, module_data: ModuleUpdate) -> Optional[ModuleResponse]:
        pass

    @abstractmethod
    async def delete(self, module_id: int) -> bool:
        pass

__all__ = ["ICourseRepository", "ILessonRepository"]