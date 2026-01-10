# services/course_service.py
from typing import List, Optional, Dict, Any
from datetime import datetime
from schemas.content import CourseContentResponse, LessonItem

from schemas import (
    CourseResponse,
    CourseDetailResponse,
    LessonResponse,
    CourseStatus,
    CourseCreate, CourseUpdate,
)

from repositories import ICourseRepository, ILessonRepository
from core.config import settings


class CourseService:
    def __init__(
        self,
        course_repo: ICourseRepository,
        lesson_repo: Optional[ILessonRepository] = None,
    ):
        self.course_repo = course_repo
        self.lesson_repo = lesson_repo
        
        if not self.lesson_repo:
            raise ValueError("lesson_repo обязателен")

    async def get_all_courses(
        self,
        status: Optional[str] = None,
        limit: int = 20,
        offset: int = 0,
        search: Optional[str] = None,
    ) -> List[CourseResponse]:
        status_enum = None
        if status:
            try:
                status_enum = CourseStatus(status)
            except ValueError:
                status_enum = None

        courses = await self.course_repo.get_all(status_enum, limit, offset, search)
        return [self._enrich_course_response(c) for c in courses]

    async def get_course_by_id(self, course_id: int) -> Optional[CourseResponse]:
        course = await self.course_repo.get_by_id(course_id)
        return self._enrich_course_response(course) if course else None

    async def get_course_detail(
        self,
        course_id: int,
        user_id: Optional[int] = None,
    ) -> Optional[CourseDetailResponse]:
        course = await self.course_repo.get_by_id(course_id)
        if not course:
            return None

        enriched_course = self._enrich_course_response(course)
        # Получаем уроки напрямую по курсу
        lessons = await self.lesson_repo.get_by_course(course_id)
        
        enriched_lessons: List[LessonResponse] = []
        for lesson in lessons:
            lesson_dict = lesson.model_dump()
            content_url = lesson_dict.get("content_url")
            if content_url and (
                content_url.startswith("/static/") or content_url.startswith("/uploads/")
            ):
                lesson_dict["content_url"] = f"{settings.SERVER_URL}{content_url}"
            enriched_lessons.append(LessonResponse(**lesson_dict))

        enrollment_info = None
        if user_id:
            enrollment_info = self._get_mock_enrollment_info(user_id, course_id)

        return CourseDetailResponse(
            **enriched_course.model_dump(),
            lessons=enriched_lessons,
            enrollment_info=enrollment_info,
        )

    async def create_course(self, course_data: CourseCreate) -> CourseResponse:
        course = await self.course_repo.create(course_data)
        return self._enrich_course_response(course)

    async def update_course(self, course_id: int, course_data: CourseUpdate) -> Optional[CourseResponse]:
        updated = await self.course_repo.update(course_id, course_data)
        return self._enrich_course_response(updated) if updated else None

    async def delete_course(self, course_id: int) -> bool:
        return await self.course_repo.delete(course_id)

    # === helpers ===
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

    async def get_course_content(self, course_id: int) -> CourseContentResponse | None:
        course = await self.course_repo.get_by_id(course_id)
        if not course:
            return None

        # course теперь CourseResponse (pydantic)
        course_id_val = course.id
        course_title = course.title
        course_desc = course.description
        course_status = course.status

        # Получаем уроки напрямую по курсу
        lessons = await self.lesson_repo.get_by_course(course_id_val)
        items = []

        for l in lessons:
            # enum -> value
            content_type = getattr(l.content_type, "value", l.content_type)
            lesson_type = getattr(l.lesson_type, "value", l.lesson_type)

            content_url = getattr(l, "content_url", None)
            if content_url and (content_url.startswith("/static/") or content_url.startswith("/uploads/")):
                content_url = f"{settings.SERVER_URL}{content_url}"

            items.append(LessonItem(
                id=l.id,
                title=l.title,
                order=l.order,
                is_published=l.is_published,
                duration_minutes=l.duration_minutes,
                content_type=content_type,
                content_text=getattr(l, "content_text", None),
                content_url=content_url,
                lesson_type=lesson_type,
            ))

        items.sort(key=lambda x: x.order)

        return CourseContentResponse(
            id=course_id_val,
            title=course_title,
            description=course_desc,
            status=course_status,
            lessons=items,
        )

    def _get_mock_enrollment_info(self, user_id: int, course_id: int) -> Dict[str, Any]:
        return {
            "enrolled_at": datetime.now().isoformat(),
            "progress_percentage": 25.0,
            "current_lesson_id": 1,
            "is_active": True,
        }
