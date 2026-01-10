from fastapi import APIRouter, Depends, HTTPException, Query, status
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from core.security import get_current_user
from core.roles import UserRole
from core.db import get_db

from schemas import LessonResponse, LessonCreate, LessonUpdate
from services import LessonService
from repositories.mock.lesson_repository import JsonLessonRepository
from repositories.mock.course_repository import JsonCourseRepository
from repositories.mock.enrollment_repository import EnrollmentRepository

router = APIRouter(prefix="/lessons", tags=["Lessons"])


async def get_lesson_service(db: AsyncSession = Depends(get_db)) -> LessonService:
    return LessonService(lesson_repo=JsonLessonRepository(db))


async def get_enrollment_repo(db: AsyncSession = Depends(get_db)) -> EnrollmentRepository:
    return EnrollmentRepository(db)


async def get_course_repo(db: AsyncSession = Depends(get_db)) -> JsonCourseRepository:
    return JsonCourseRepository(db)


async def check_lesson_access(
    lesson,
    current_user: dict,
    course_repo: JsonCourseRepository,
    enrollment_repo: EnrollmentRepository,
):
    role = current_user["role"]
    user_id = current_user["id"]

    course_id = lesson.course_id

    if role in (UserRole.ADMIN.value, UserRole.MANAGER.value):
        return

    if role == UserRole.TRAINER.value:
        teacher_courses = await enrollment_repo.get_courses_for_teacher(user_id)
        if course_id not in teacher_courses:
            raise HTTPException(status_code=403, detail="У вас нет доступа к уроку")
        return

    if role == UserRole.STUDENT.value:
        student_courses = await enrollment_repo.get_courses_for_student(user_id)
        if course_id not in student_courses:
            raise HTTPException(status_code=403, detail="У вас нет доступа к уроку")

        if not lesson.is_published:
            raise HTTPException(status_code=403, detail="Урок недоступен")

        return

    raise HTTPException(status_code=403, detail="Недостаточно прав")


@router.get("/", response_model=List[LessonResponse])
async def get_lessons(
    course_id: Optional[int] = Query(None),
    lesson_type: Optional[str] = Query(None),

    service: LessonService = Depends(get_lesson_service),
    enrollment_repo: EnrollmentRepository = Depends(get_enrollment_repo),
    current_user: dict = Depends(get_current_user),
):
    lessons = await service.get_all_lessons(course_id=course_id, lesson_type=lesson_type)

    role = current_user["role"]
    user_id = current_user["id"]

    filtered = []

    for lesson in lessons:
        course_id = lesson.course_id
        if role in (UserRole.ADMIN.value, UserRole.MANAGER.value):
            filtered.append(lesson)
            continue
        if role == UserRole.TRAINER.value:
            teacher_courses = await enrollment_repo.get_courses_for_teacher(user_id)
            if course_id in teacher_courses:
                filtered.append(lesson)
            continue
        if role == UserRole.STUDENT.value:
            student_courses = await enrollment_repo.get_courses_for_student(user_id)
            if course_id in student_courses:
                if lesson.is_published:
                    filtered.append(lesson)
            continue

    return filtered

@router.get("/{lesson_id}", response_model=LessonResponse)
async def get_lesson(
    lesson_id: int,

    service: LessonService = Depends(get_lesson_service),
    course_repo: JsonCourseRepository = Depends(get_course_repo),
    enrollment_repo: EnrollmentRepository = Depends(get_enrollment_repo),
    current_user: dict = Depends(get_current_user),
):
    lesson = await service.get_lesson_by_id(lesson_id)
    if not lesson:
        raise HTTPException(status_code=404, detail="Урок не найден")

    await check_lesson_access(lesson, current_user, course_repo, enrollment_repo)

    return lesson

@router.post("/", response_model=LessonResponse, status_code=201)
async def create_lesson(
    lesson_data: LessonCreate,

    service: LessonService = Depends(get_lesson_service),
    current_user: dict = Depends(get_current_user),
):
    if current_user["role"] not in (UserRole.ADMIN.value, UserRole.MANAGER.value):
        raise HTTPException(status_code=403, detail="Недостаточно прав")

    return await service.create_lesson(lesson_data)

@router.patch("/{lesson_id}", response_model=LessonResponse)
async def update_lesson(
    lesson_id: int,
    lesson_data: LessonUpdate,

    service: LessonService = Depends(get_lesson_service),
    current_user: dict = Depends(get_current_user),
):
    if current_user["role"] not in (UserRole.ADMIN.value, UserRole.MANAGER.value):
        raise HTTPException(status_code=403, detail="Недостаточно прав")

    updated = await service.update_lesson(lesson_id, lesson_data)
    if not updated:
        raise HTTPException(status_code=404, detail="Урок не найден")

    return updated

@router.delete("/{lesson_id}", status_code=204)
async def delete_lesson(
    lesson_id: int,

    service: LessonService = Depends(get_lesson_service),
    current_user: dict = Depends(get_current_user),
):
    if current_user["role"] not in (UserRole.ADMIN.value, UserRole.MANAGER.value):
        raise HTTPException(status_code=403, detail="Недостаточно прав")

    success = await service.delete_lesson(lesson_id)
    if not success:
        raise HTTPException(status_code=404, detail="Урок не найден")

    return None
