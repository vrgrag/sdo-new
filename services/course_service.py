# 📁 services/course_service.py
from typing import List, Optional, Dict, Any
from datetime import datetime
from schemas import (
    CourseResponse,
    CourseDetailResponse,
    ModuleResponse,
    LessonResponse,
    CourseStatus, CourseCreate
)
from repositories import ICourseRepository, MockModuleRepository, MockLessonRepository
from core.config import settings


class CourseService:
    def __init__(
            self,
            course_repo: ICourseRepository,
            module_repo: Optional[MockModuleRepository] = None,
            lesson_repo: Optional[MockLessonRepository] = None,
    ):
        self.course_repo = course_repo
        self.module_repo = module_repo or MockModuleRepository()
        self.lesson_repo = lesson_repo or MockLessonRepository()

    def get_all_courses(
            self,
            status: Optional[str] = None,  # ← изменил с CourseStatus на str
            limit: int = 20,
            offset: int = 0,
            search: Optional[str] = None
    ) -> List[CourseResponse]:

        status_enum = None
        if status:
            try:
                status_enum = CourseStatus(status)
            except ValueError:
                pass

        courses = self.course_repo.get_all(status_enum, limit, offset, search)
        return [self._enrich_course_response(c) for c in courses]

    def get_course_by_id(self, course_id: int) -> Optional[CourseResponse]:
        course = self.course_repo.get_by_id(course_id)
        return self._enrich_course_response(course) if course else None

    def get_course_detail(
            self,
            course_id: int,
            user_id: Optional[int] = None
    ) -> Optional[CourseDetailResponse]:


        course = self.course_repo.get_by_id(course_id)
        if not course:
            return None

        enriched_course = self._enrich_course_response(course)

        modules = self._get_modules_with_lessons(course_id)

        enrollment_info = None
        if user_id:
            enrollment_info = self._get_mock_enrollment_info(user_id, course_id)

        return CourseDetailResponse(
            **enriched_course.model_dump(),
            modules=modules,
            enrollment_info=enrollment_info
        )

    def create_course(self, course_data: CourseCreate) -> CourseResponse:

        course = self.course_repo.create(course_data)
        return self._enrich_course_response(course)

    # === ВСПОМОГАТЕЛЬНЫЕ МЕТОДЫ ===
    def _enrich_course_response(self, course: CourseResponse) -> CourseResponse:

        if not course:
            return course

        data = course.model_dump()

        image_url = data.get("image_url")
        if image_url:
            if image_url.startswith("/static/") or image_url.startswith("/uploads/"):
                data["image_url"] = f"{settings.SERVER_URL}{image_url}"
        else:
            data["image_url"] = f"{settings.SERVER_URL}{settings.STATIC_URL}/default_course_image.jpg"

        return CourseResponse(**data)

    def _get_modules_with_lessons(self, course_id: int) -> List[ModuleResponse]:

        modules = self.module_repo.get_by_course(course_id)

        for module in modules:
            lessons = self.lesson_repo.get_by_module(module.id)

            enriched_lessons = []
            for lesson in lessons:
                lesson_dict = lesson.model_dump()

                content_url = lesson_dict.get("content_url")
                if content_url and (content_url.startswith("/static/") or content_url.startswith("/uploads/")):
                    lesson_dict["content_url"] = f"{settings.SERVER_URL}{content_url}"

                enriched_lessons.append(LessonResponse(**lesson_dict))

            module.lessons = enriched_lessons

        return modules

    def _get_mock_enrollment_info(self, user_id: int, course_id: int) -> Dict[str, Any]:

        return {
            "enrolled_at": datetime.now().isoformat(),
            "progress_percentage": 25.0,
            "current_lesson_id": 1,
            "is_active": True
        }