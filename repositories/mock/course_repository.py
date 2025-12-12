# 📁 repositories/mock/course_repository.py
from datetime import datetime
from typing import List, Optional
import json
import os

from repositories.base import ICourseRepository
from schemas import CourseResponse, CourseCreate, CourseUpdate, CourseStatus


MOCK_COURSES = []

DATA_FILE = "db/courses.json"
os.makedirs("db", exist_ok=True)


def _load_courses_from_file() -> list[dict]:
    if not os.path.exists(DATA_FILE):
        return []

    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return []


def _save_courses_to_file(courses: list[dict]) -> None:
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(courses, f, ensure_ascii=False, indent=2)


class JsonCourseRepository(ICourseRepository):
    def __init__(self):
        file_courses = _load_courses_from_file()

        self._courses: dict[int, dict] = {c["id"]: c for c in file_courses} if file_courses else {}
        self._id_counter = (max(self._courses.keys()) + 1) if self._courses else 1

        _save_courses_to_file(list(self._courses.values()))

        if file_courses:
            self._courses: dict[int, dict] = {c["id"]: c for c in file_courses}
            self._id_counter = max(self._courses.keys()) + 1
        else:

            self._courses = {}
            for course in MOCK_COURSES:
                c = course.copy()

                for field in ("created_at", "updated_at"):
                    if isinstance(c.get(field), datetime):
                        c[field] = c[field].isoformat()

                self._courses[c["id"]] = c

            if self._courses:
                self._id_counter = max(self._courses.keys()) + 1
            else:
                self._id_counter = 1

            _save_courses_to_file(list(self._courses.values()))


    def get_all(
            self,
            status: Optional[CourseStatus] = None,
            limit: int = 20,
            offset: int = 0,
            search: Optional[str] = None
    ) -> List[CourseResponse]:
        courses = list(self._courses.values())

        if status is not None:
            courses = [c for c in courses if c.get("status") == status.value]

        if search:
            q = search.lower()
            courses = [
                c for c in courses
                if q in c.get("title", "").lower()
                or q in (c.get("description") or "").lower()
            ]

        courses.sort(key=lambda x: x.get("created_at", ""), reverse=True)

        paginated = courses[offset:offset + limit]
        return [self._dict_to_response(c) for c in paginated]

    def get_by_id(self, course_id: int) -> Optional[CourseResponse]:
        course_dict = self._courses.get(course_id)
        if course_dict is None:
            return None
        return self._dict_to_response(course_dict)


    def create(self, course_data: CourseCreate) -> CourseResponse:
        now = datetime.now().isoformat()

        course_id = self._id_counter
        self._id_counter += 1

        course_dict = {
            "id": course_id,
            "title": course_data.title,
            "description": course_data.description,
            "short_description": course_data.short_description,
            "status": CourseStatus.DRAFT.value,  # при создании — черновик
            "image_url": course_data.image_url,
            "default_image_url": "/static/default_course_image.jpg",
            "duration_hours": course_data.duration_hours or 0,
            "created_by_id": 1,  # TODO: потом взять из current_user
            "assigned_manager_id": None,
            "created_at": now,
            "updated_at": now,
            "tags": course_data.tags or [],
            "requirements": course_data.requirements or [],
            "what_you_learn": course_data.what_you_learn or [],
            "enrollment_status": "available",
        }

        self._courses[course_id] = course_dict
        _save_courses_to_file(list(self._courses.values()))

        return self._dict_to_response(course_dict)


    def update(self, course_id: int, course_data: CourseUpdate) -> Optional[CourseResponse]:
        course_dict = self._courses.get(course_id)
        if course_dict is None:
            return None

        update_data = course_data.model_dump(exclude_unset=True)

        for key, value in update_data.items():
            if value is None:
                continue

            if key == "status" and isinstance(value, CourseStatus):
                # в JSON храним строку
                course_dict[key] = value.value
            else:
                course_dict[key] = value

        course_dict["updated_at"] = datetime.now().isoformat()
        self._courses[course_id] = course_dict
        _save_courses_to_file(list(self._courses.values()))

        return self._dict_to_response(course_dict)

    def delete(self, course_id: int) -> bool:
        if course_id in self._courses:
            del self._courses[course_id]
            _save_courses_to_file(list(self._courses.values()))
            return True
        return False

    def get_courses_by_trainer(self, trainer_id: int) -> List[dict]:

        from repositories.mock.enrollment_repository import EnrollmentRepository

        enrollment_repo = EnrollmentRepository()
        course_ids = enrollment_repo.get_courses_for_trainer(trainer_id)

        result: List[dict] = []
        for cid in course_ids:
            course = self._courses.get(cid)
            if course:
                result.append(course)
        return result

    def get_courses_by_teacher(self, teacher_id: int) -> List[dict]:
        return self.get_courses_by_trainer(teacher_id)

    def get_students_by_course(self, course_id: int) -> List[dict]:

        from repositories.mock.enrollment_repository import EnrollmentRepository
        from repositories.mock.user_repository import user_repository

        enrollment_repo = EnrollmentRepository()
        all_users = user_repository.get_all()

        students_ids = set()
        for u in all_users:
            if u.get("role") != "student":
                continue
            uid = u.get("id")
            if uid is None:
                continue
            if course_id in enrollment_repo.get_courses_for_student(uid):
                students_ids.add(uid)

        return [u for u in all_users if u.get("id") in students_ids]

    def _dict_to_response(self, course_dict: dict) -> CourseResponse:
        data = course_dict.copy()

        for key in list(data.keys()):
            if key not in CourseResponse.model_fields:
                data.pop(key, None)

        return CourseResponse(**data)
