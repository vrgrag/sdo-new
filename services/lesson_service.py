# services/lesson_service.py
from typing import List, Optional
from schemas import LessonResponse, LessonCreate, LessonUpdate
from repositories import ILessonRepository
from core.config import settings

class LessonService:
    def __init__(self, lesson_repo: ILessonRepository):
        self.lesson_repo = lesson_repo

    async def get_all_lessons(
        self,
        course_id: Optional[int] = None,
        lesson_type: Optional[str] = None
    ) -> List[LessonResponse]:
        lessons = await self.lesson_repo.get_all(course_id, lesson_type)
        return [self._enrich_lesson(l) for l in lessons]

    async def get_lesson_by_id(self, lesson_id: int) -> Optional[LessonResponse]:
        lesson = await self.lesson_repo.get_by_id(lesson_id)
        return self._enrich_lesson(lesson) if lesson else None

    async def create_lesson(self, lesson_data: LessonCreate) -> LessonResponse:
        lesson = await self.lesson_repo.create(lesson_data)
        return self._enrich_lesson(lesson)

    async def update_lesson(self, lesson_id: int, lesson_data: LessonUpdate) -> Optional[LessonResponse]:
        updated = await self.lesson_repo.update(lesson_id, lesson_data)
        return self._enrich_lesson(updated) if updated else None

    async def delete_lesson(self, lesson_id: int) -> bool:
        return await self.lesson_repo.delete(lesson_id)

    def _enrich_lesson(self, lesson: LessonResponse) -> LessonResponse:
        if not lesson or not lesson.content_url:
            return lesson
        url = lesson.content_url
        if url.startswith("/uploads/") or url.startswith("/static/"):
            lesson.content_url = f"{settings.SERVER_URL}{url}"
        return lesson