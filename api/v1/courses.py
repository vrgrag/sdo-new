from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional

from core.security import get_current_user
from core.roles import UserRole

from schemas import (
    CourseResponse,
    CourseDetailResponse,
    CourseCreate,
    CourseUpdate,
)

from services import CourseService
from repositories import (
    MockCourseRepository,
    MockModuleRepository,
    MockLessonRepository,
)
from repositories.mock.enrollment_repository import EnrollmentRepository

router = APIRouter(prefix="/courses", tags=["Courses"])


def get_course_service() -> CourseService:
    return CourseService(
        course_repo=MockCourseRepository(),
        module_repo=MockModuleRepository(),
        lesson_repo=MockLessonRepository(),
    )


def get_enrollment_repo() -> EnrollmentRepository:
    return EnrollmentRepository()


@router.get("/", response_model=List[CourseResponse])
async def list_courses(
    status: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    limit: int = Query(20),
    offset: int = Query(0),
    service: CourseService = Depends(get_course_service),
    enrollment_repo: EnrollmentRepository = Depends(get_enrollment_repo),
    current_user: dict = Depends(get_current_user),
):
    user_id = current_user["id"]
    role = current_user["role"]

    all_courses = service.get_all_courses(status, limit, offset, search)

    if role == UserRole.STUDENT.value:
        allowed = set(enrollment_repo.get_courses_for_student(user_id))
        return [c for c in all_courses if c.id in allowed]

    if role == UserRole.TRAINER.value:
        allowed = set(enrollment_repo.get_courses_for_trainer(user_id))
        return [c for c in all_courses if c.id in allowed]

    return all_courses


@router.get("/{course_id}", response_model=CourseDetailResponse)
async def course_detail(
    course_id: int,
    service: CourseService = Depends(get_course_service),
    enrollment_repo: EnrollmentRepository = Depends(get_enrollment_repo),
    current_user: dict = Depends(get_current_user),
):
    user_id = current_user["id"]
    role = current_user["role"]

    course = service.get_course_detail(course_id, user_id)
    if not course:
        raise HTTPException(status_code=404, detail="Курс не найден")

    if role == UserRole.STUDENT.value:
        if course_id not in enrollment_repo.get_courses_for_student(user_id):
            raise HTTPException(status_code=403, detail="Нет доступа")

    if role == UserRole.TRAINER.value:
        if course_id not in enrollment_repo.get_courses_for_trainer(user_id):
            raise HTTPException(status_code=403, detail="Нет доступа")

    return course


@router.post("/", response_model=CourseResponse, status_code=201)
async def create_course(
    course_data: CourseCreate,
    service: CourseService = Depends(get_course_service),
    current_user: dict = Depends(get_current_user),
):
    if current_user["role"] not in (UserRole.ADMIN.value, UserRole.MANAGER.value):
        raise HTTPException(status_code=403, detail="Недостаточно прав")

    return service.create_course(course_data)


@router.patch("/{course_id}", response_model=CourseResponse)
async def update_course(
    course_id: int,
    course_data: CourseUpdate,
    service: CourseService = Depends(get_course_service),
    current_user: dict = Depends(get_current_user),
):
    if current_user["role"] not in (UserRole.ADMIN.value, UserRole.MANAGER.value):
        raise HTTPException(status_code=403, detail="Недостаточно прав")

    updated = service.course_repo.update(course_id, course_data)
    if not updated:
        raise HTTPException(status_code=404, detail="Курс не найден")

    return service._enrich_course_response(updated)


@router.delete("/{course_id}", status_code=204)
async def delete_course(
    course_id: int,
    service: CourseService = Depends(get_course_service),
    current_user: dict = Depends(get_current_user),
):
    if current_user["role"] not in (UserRole.ADMIN.value, UserRole.MANAGER.value):
        raise HTTPException(status_code=403, detail="Недостаточно прав")

    deleted = service.course_repo.delete(course_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Курс не найден")

    return None


@router.post("/{course_id}/students/{student_id}", status_code=204)
async def assign_student(
    course_id: int,
    student_id: int,
    enrollment_repo: EnrollmentRepository = Depends(get_enrollment_repo),
    current_user: dict = Depends(get_current_user),
):
    role = current_user["role"]
    user_id = current_user["id"]

    if role in (UserRole.ADMIN.value, UserRole.MANAGER.value):
        enrollment_repo.enroll_student(student_id, course_id)
        return None

    if role == UserRole.TRAINER.value:
        trainer_courses = enrollment_repo.get_courses_for_trainer(user_id)
        if course_id not in trainer_courses:
            raise HTTPException(status_code=403, detail="Вы не являетесь тренером курса")
        enrollment_repo.enroll_student(student_id, course_id)
        return None

    raise HTTPException(status_code=403, detail="Недостаточно прав")


@router.post("/{course_id}/trainers/{trainer_id}", status_code=204)
async def assign_trainer(
    course_id: int,
    trainer_id: int,
    enrollment_repo: EnrollmentRepository = Depends(get_enrollment_repo),
    current_user: dict = Depends(get_current_user),
):
    if current_user["role"] not in (UserRole.ADMIN.value, UserRole.MANAGER.value):
        raise HTTPException(status_code=403, detail="Недостаточно прав")

    enrollment_repo.assign_trainer(trainer_id, course_id)
    return None
