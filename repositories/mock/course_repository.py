# 📁 repositories/mock/course_repository.py
from datetime import datetime
from typing import List, Optional
from sqlalchemy import select, or_, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from repositories.base import ICourseRepository
from schemas import CourseResponse, CourseCreate, CourseUpdate, CourseStatus
from models.courses import Courses


class JsonCourseRepository(ICourseRepository):
    def __init__(self, db: AsyncSession):
        self.db = db


    def _to_response(self, course: Courses) -> CourseResponse:
        """Преобразует модель Courses в CourseResponse"""
        # Преобразуем статус из строки в enum
        status_value = course.status if isinstance(course.status, str) else (
            CourseStatus.PUBLISHED.value if course.status else CourseStatus.DRAFT.value
        )
        try:
            status = CourseStatus(status_value)
        except ValueError:
            status = CourseStatus.DRAFT

        return CourseResponse(
            id=course.id,
            title=course.title,
            description=course.description or "",
            short_description=course.short_description,
            image_url=course.image,
            duration_hours=course.duration_hours or 0,
            tags=course.tags if course.tags else [],
            requirements=course.requirements if course.requirements else [],
            what_you_learn=course.what_you_learn if course.what_you_learn else [],
            status=status,
        )

    async def get_all(
            self,
            status: Optional[CourseStatus] = None,
            limit: int = 20,
            offset: int = 0,
            search: Optional[str] = None
    ) -> List[CourseResponse]:
        stmt = select(Courses)

        # Фильтр по статусу
        if status is not None:
            stmt = stmt.where(Courses.status == status.value)

        # Поиск
        if search:
            search_lower = search.lower()
            stmt = stmt.where(
                or_(
                    func.lower(Courses.title).contains(search_lower),
                    func.lower(Courses.description).contains(search_lower),
                )
            )

        # Сортировка по дате создания (новые первые)
        stmt = stmt.order_by(Courses.created_at.desc())

        # Пагинация
        stmt = stmt.limit(limit).offset(offset)

        res = await self.db.execute(stmt)
        courses = res.scalars().all()
        return [self._to_response(c) for c in courses]

    async def get_by_id(self, course_id: int) -> Optional[CourseResponse]:
        course = await self.db.get(Courses, course_id)
        if not course:
            return None
        return self._to_response(course)


    async def create(self, course_data: CourseCreate) -> CourseResponse:
        now = datetime.utcnow()

        course = Courses(
            title=course_data.title,
            description=course_data.description,
            short_description=course_data.short_description,
            status=CourseStatus.DRAFT.value,  # при создании — черновик
            image=course_data.image_url,
            duration_hours=course_data.duration_hours or 0,
            tags=course_data.tags or [],
            requirements=course_data.requirements or [],
            what_you_learn=course_data.what_you_learn or [],
            created_at=now,
            updated_at=now,
        )

        self.db.add(course)
        try:
            await self.db.commit()
        except IntegrityError:
            await self.db.rollback()
            raise
        await self.db.refresh(course)
        return self._to_response(course)


    async def update(self, course_id: int, course_data: CourseUpdate) -> Optional[CourseResponse]:
        course = await self.db.get(Courses, course_id)
        if not course:
            return None

        update_data = course_data.model_dump(exclude_unset=True)

        for key, value in update_data.items():
            if value is None and key not in ["short_description", "image_url"]:  # разрешаем None для опциональных полей
                continue

            if key == "status" and isinstance(value, CourseStatus):
                setattr(course, "status", value.value)
            elif key == "image_url":
                setattr(course, "image", value)
            else:
                setattr(course, key, value)

        course.updated_at = datetime.utcnow()

        try:
            await self.db.commit()
        except IntegrityError:
            await self.db.rollback()
            raise

        await self.db.refresh(course)
        return self._to_response(course)

    async def delete(self, course_id: int) -> bool:
        course = await self.db.get(Courses, course_id)
        if not course:
            return False
        await self.db.delete(course)
        await self.db.commit()
        return True

    async def get_courses_by_trainer(self, trainer_id: int) -> List[dict]:
        from repositories.mock.enrollment_repository import EnrollmentRepository

        enrollment_repo = EnrollmentRepository(self.db)
        course_ids = await enrollment_repo.get_courses_for_trainer(trainer_id)

        if not course_ids:
            return []

        stmt = select(Courses).where(Courses.id.in_(course_ids))
        res = await self.db.execute(stmt)
        courses = res.scalars().all()
        
        return [self._to_response(c).model_dump() for c in courses]

    async def get_courses_by_teacher(self, teacher_id: int) -> List[dict]:
        return await self.get_courses_by_trainer(teacher_id)

    async def get_students_by_course(self, course_id: int) -> List[dict]:
        from repositories.mock.enrollment_repository import EnrollmentRepository
        from repositories.mock.user_repository import UserRepository

        enrollment_repo = EnrollmentRepository(self.db)
        user_repo = UserRepository(self.db)
        all_users = await user_repo.get_all()

        students_ids = set()
        for u in all_users:
            if u.get("role") != "student":
                continue
            uid = u.get("id")
            if uid is None:
                continue
            student_courses = await enrollment_repo.get_courses_for_student(uid)
            if course_id in student_courses:
                students_ids.add(uid)

        return [u for u in all_users if u.get("id") in students_ids]
