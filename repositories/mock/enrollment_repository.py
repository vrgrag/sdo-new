# repositories/mock/enrollment_repository.py
from typing import List
from sqlalchemy import select, and_, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from models.course_enrollments import CourseEnrollment


class EnrollmentRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def enroll_student(self, student_id: int, course_id: int) -> None:
        """Записать студента на курс"""
        # Проверяем, нет ли уже такой записи
        stmt = select(CourseEnrollment).where(
            and_(
                CourseEnrollment.user_id == student_id,
                CourseEnrollment.course_id == course_id,
                CourseEnrollment.enrollment_type == "student"
            )
        )
        result = await self.db.execute(stmt)
        existing = result.scalar_one_or_none()
        
        if existing:
            return  # Уже записан
        
        enrollment = CourseEnrollment(
            user_id=student_id,
            course_id=course_id,
            enrollment_type="student"
        )
        self.db.add(enrollment)
        try:
            await self.db.commit()
        except IntegrityError:
            await self.db.rollback()
            raise

    async def unenroll_student(self, student_id: int, course_id: int) -> None:
        """Отписать студента с курса"""
        stmt = delete(CourseEnrollment).where(
            and_(
                CourseEnrollment.user_id == student_id,
                CourseEnrollment.course_id == course_id,
                CourseEnrollment.enrollment_type == "student"
            )
        )
        await self.db.execute(stmt)
        await self.db.commit()

    async def get_courses_for_student(self, student_id: int) -> List[int]:
        """Получить список ID курсов, на которые записан студент"""
        stmt = select(CourseEnrollment.course_id).where(
            and_(
                CourseEnrollment.user_id == student_id,
                CourseEnrollment.enrollment_type == "student"
            )
        )
        result = await self.db.execute(stmt)
        return [row[0] for row in result.all()]

    async def assign_trainer(self, trainer_id: int, course_id: int) -> None:
        """Назначить тренера на курс"""
        # Проверяем, нет ли уже такой записи
        stmt = select(CourseEnrollment).where(
            and_(
                CourseEnrollment.user_id == trainer_id,
                CourseEnrollment.course_id == course_id,
                CourseEnrollment.enrollment_type == "trainer"
            )
        )
        result = await self.db.execute(stmt)
        existing = result.scalar_one_or_none()
        
        if existing:
            return  # Уже назначен
        
        enrollment = CourseEnrollment(
            user_id=trainer_id,
            course_id=course_id,
            enrollment_type="trainer"
        )
        self.db.add(enrollment)
        try:
            await self.db.commit()
        except IntegrityError:
            await self.db.rollback()
            raise

    async def unassign_trainer(self, trainer_id: int, course_id: int) -> None:
        """Снять тренера с курса"""
        stmt = delete(CourseEnrollment).where(
            and_(
                CourseEnrollment.user_id == trainer_id,
                CourseEnrollment.course_id == course_id,
                CourseEnrollment.enrollment_type == "trainer"
            )
        )
        await self.db.execute(stmt)
        await self.db.commit()

    async def get_courses_for_trainer(self, trainer_id: int) -> List[int]:
        """Получить список ID курсов, которые ведет тренер"""
        stmt = select(CourseEnrollment.course_id).where(
            and_(
                CourseEnrollment.user_id == trainer_id,
                CourseEnrollment.enrollment_type == "trainer"
            )
        )
        result = await self.db.execute(stmt)
        return [row[0] for row in result.all()]

    # Алиасы для обратной совместимости
    async def assign_teacher(self, teacher_id: int, course_id: int) -> None:
        """Алиас для assign_trainer (обратная совместимость)"""
        return await self.assign_trainer(teacher_id, course_id)

    async def unassign_teacher(self, teacher_id: int, course_id: int) -> None:
        """Алиас для unassign_trainer (обратная совместимость)"""
        return await self.unassign_trainer(teacher_id, course_id)

    async def get_courses_for_teacher(self, teacher_id: int) -> List[int]:
        """Алиас для get_courses_for_trainer (обратная совместимость)"""
        return await self.get_courses_for_trainer(teacher_id)
