from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from repositories.base import ILessonRepository
from schemas import LessonResponse, LessonCreate, LessonUpdate
from schemas.common import ContentType, LessonType
from models.lessons import Lessons


class JsonLessonRepository(ILessonRepository):
    def __init__(self, db: AsyncSession):
        self.db = db

    def _to_response(self, lesson: Lessons) -> LessonResponse:
        """Преобразует модель Lessons в LessonResponse"""
        # Преобразуем строки в enum
        try:
            content_type = ContentType(lesson.content_type)
        except ValueError:
            content_type = ContentType.TEXT

        try:
            lesson_type = LessonType(lesson.lesson_type)
        except ValueError:
            lesson_type = LessonType.THEORY

        return LessonResponse(
            id=lesson.id,
            course_id=lesson.course_id,
            title=lesson.title,
            content_type=content_type,
            content_url=lesson.content_url,
            content_text=lesson.content_text,
            duration_minutes=lesson.duration_minutes,
            order=lesson.order,
            lesson_type=lesson_type,
            is_published=lesson.is_published,
        )

    async def get_all(
        self,
        course_id: Optional[int] = None,
        lesson_type: Optional[str] = None
    ) -> List[LessonResponse]:
        stmt = select(Lessons)

        if course_id is not None:
            stmt = stmt.where(Lessons.course_id == course_id)

        if lesson_type is not None:
            stmt = stmt.where(Lessons.lesson_type == lesson_type)

        stmt = stmt.order_by(Lessons.course_id.asc(), Lessons.order.asc())

        res = await self.db.execute(stmt)
        lessons = res.scalars().all()
        return [self._to_response(l) for l in lessons]

    async def get_by_id(self, lesson_id: int) -> Optional[LessonResponse]:
        lesson = await self.db.get(Lessons, lesson_id)
        if not lesson:
            return None
        return self._to_response(lesson)

    async def get_by_course(self, course_id: int) -> List[LessonResponse]:
        stmt = (
            select(Lessons)
            .where(Lessons.course_id == course_id)
            .order_by(Lessons.order.asc())
        )
        res = await self.db.execute(stmt)
        lessons = res.scalars().all()
        return [self._to_response(l) for l in lessons]

    async def create(self, lesson: LessonCreate) -> LessonResponse:
        lesson_obj = Lessons(
            course_id=lesson.course_id,
            title=lesson.title,
            content_type=lesson.content_type.value,
            content_url=lesson.content_url,
            content_text=lesson.content_text,
            duration_minutes=lesson.duration_minutes,
            order=lesson.order,
            lesson_type=lesson.lesson_type.value,
            is_published=lesson.is_published,
        )
        self.db.add(lesson_obj)
        try:
            await self.db.commit()
        except IntegrityError:
            await self.db.rollback()
            raise
        await self.db.refresh(lesson_obj)
        return self._to_response(lesson_obj)

    async def update(
        self,
        lesson_id: int,
        lesson_data: LessonUpdate
    ) -> Optional[LessonResponse]:
        lesson = await self.db.get(Lessons, lesson_id)
        if not lesson:
            return None

        update_data = lesson_data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            if value is None:
                continue

            if key == "content_type" and isinstance(value, ContentType):
                setattr(lesson, key, value.value)
            elif key == "lesson_type" and isinstance(value, LessonType):
                setattr(lesson, key, value.value)
            else:
                setattr(lesson, key, value)

        try:
            await self.db.commit()
        except IntegrityError:
            await self.db.rollback()
            raise

        await self.db.refresh(lesson)
        return self._to_response(lesson)

    async def delete(self, lesson_id: int) -> bool:
        lesson = await self.db.get(Lessons, lesson_id)
        if not lesson:
            return False
        await self.db.delete(lesson)
        await self.db.commit()
        return True
