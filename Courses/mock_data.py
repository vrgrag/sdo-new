from datetime import datetime, timedelta
import uuid
from typing import Dict, List, Optional
from database import CourseStatus, ContentType, LessonType, UserRole

# --- Mock базы данных ---
mock_users_db: Dict[int, Dict] = {}
mock_courses_db: Dict[int, Dict] = {}
mock_modules_db: Dict[int, Dict] = {}
mock_lessons_db: Dict[int, Dict] = {}
mock_tests_db: Dict[int, Dict] = {}
mock_enrollments_db: Dict[int, Dict] = {}
mock_progress_db: Dict[int, Dict] = {}

# ID счетчики
user_id_counter = 1
course_id_counter = 1
module_id_counter = 1
lesson_id_counter = 1
test_id_counter = 1
enrollment_id_counter = 1
progress_id_counter = 1


# --- Функции для работы с заглушками ---

def init_mock_data():
    """Инициализировать тестовые данные"""
    global mock_users_db, mock_courses_db, user_id_counter, course_id_counter

    # Создаем тестовых пользователей
    admin_user = create_mock_user(
        email="admin@example.com",
        full_name="Администратор Системы",
        role=UserRole.ADMIN,
        avatar_url="/static/avatars/admin.jpg"
    )

    manager_user = create_mock_user(
        email="manager@example.com",
        full_name="Менеджер Курсов",
        role=UserRole.MANAGER,
        avatar_url="/static/avatars/manager.jpg"
    )

    teacher_user = create_mock_user(
        email="teacher@example.com",
        full_name="Преподаватель Эксперт",
        role=UserRole.TEACHER,
        avatar_url="/static/avatars/teacher.jpg"
    )

    student_user = create_mock_user(
        email="student@example.com",
        full_name="Иван Студентов",
        role=UserRole.STUDENT,
        avatar_url="/static/avatars/student.jpg"
    )

    # Создаем тестовые курсы
    course_1ak = create_mock_course(
        title="1AK - Профессиональный курс",
        description="Полный курс по 1AK с практическими заданиями и проектами. Изучите все аспекты технологии от основ до продвинутых техник.",
        short_description="Освойте 1AK с нуля до профессионального уровня",
        code="1AK",
        created_by_id=admin_user["id"],
        assigned_manager_id=manager_user["id"],
        status=CourseStatus.PUBLISHED,
        image_url="/static/course_images/1ak_course.jpg",
        duration_hours=120,
        tags=["1AK", "профессиональные навыки", "практика", "сертификация"],
        requirements=["Базовые знания предметной области", "Навыки работы с ПК"],
        what_you_learn=["Понимание основных принципов 1AK", "Практические навыки применения", "Решение реальных задач"],
        # Добавляем поле для отображения вместо "Записано"
        enrollment_status="available"
    )

    python_course = create_mock_course(
        title="Python для начинающих",
        description="Изучите Python с нуля: синтаксис, структуры данных, ООП, работа с файлами и базами данных.",
        short_description="Основы программирования на Python",
        code="PY101",
        created_by_id=teacher_user["id"],
        status=CourseStatus.PUBLISHED,
        image_url="/static/course_images/python_course.jpg",
        duration_hours=60,
        tags=["Python", "программирование", "начинающим", "backend"],
        requirements=["Базовые знания компьютера"],
        what_you_learn=["Основы Python", "ООП", "Работа с файлами", "Основы алгоритмов"],
        enrollment_status="available"
    )

    # Создаем модули для курса 1AK
    module1 = create_mock_module(
        course_id=course_1ak["id"],
        title="Введение в 1AK",
        description="Основные концепции и введение в технологию",
        order=1
    )

    module2 = create_mock_module(
        course_id=course_1ak["id"],
        title="Практическая часть",
        description="Применение технологии на практике",
        order=2
    )

    # Создаем уроки для модулей
    lesson1 = create_mock_lesson(
        module_id=module1["id"],
        title="Что такое 1AK?",
        content_type=ContentType.VIDEO,
        content_url="/uploads/videos/1ak_intro.mp4",
        duration_minutes=30,
        order=1
    )

    lesson2 = create_mock_lesson(
        module_id=module1["id"],
        title="Основные принципы работы",
        content_type=ContentType.PDF,
        content_url="/uploads/pdfs/1ak_principles.pdf",
        content_text="В этом уроке мы рассмотрим основные принципы...",
        duration_minutes=45,
        order=2
    )

    lesson3 = create_mock_lesson(
        module_id=module2["id"],
        title="Практическое задание",
        content_type=ContentType.TEXT,
        content_text="Выполните следующие шаги для практического применения...",
        lesson_type=LessonType.PRACTICE,
        duration_minutes=60,
        order=1
    )

    # Создаем тест
    test1 = create_mock_test(
        module_id=module1["id"],
        title="Тест по основам 1AK",
        description="Проверьте свои знания по пройденному материалу",
        questions=[
            {
                "id": "q1",
                "question": "Что означает аббревиатура 1AK?",
                "options": ["Первая автоматическая компания", "Единая автоматизированная система",
                            "Интегрированный аналитический комплекс"],
                "correct_answer": "Интегрированный аналитический комплекс",
                "points": 10
            },
            {
                "id": "q2",
                "question": "Основное назначение 1AK?",
                "options": ["Развлечение", "Автоматизация бизнес-процессов", "Графический дизайн"],
                "correct_answer": "Автоматизация бизнес-процессов",
                "points": 10
            }
        ]
    )

    # Записываем студента на курс (но это не отображается в API)
    enrollment = create_mock_enrollment(
        user_id=student_user["id"],
        course_id=course_1ak["id"]
    )

    # Добавляем прогресс
    create_mock_progress(
        enrollment_id=enrollment["id"],
        lesson_id=lesson1["id"],
        is_completed=True,
        time_spent_minutes=35
    )

    return {
        "users_count": len(mock_users_db),
        "courses_count": len(mock_courses_db),
        "modules_count": len(mock_modules_db),
        "lessons_count": len(mock_lessons_db),

    }


# --- CRUD операции для заглушек ---

def create_mock_user(
        email: str,
        full_name: str,
        role: UserRole = UserRole.STUDENT,
        avatar_url: Optional[str] = None
) -> Dict:
    """Создать мок-пользователя"""
    global user_id_counter, mock_users_db

    user_id = user_id_counter
    user_id_counter += 1

    user = {
        "id": user_id,
        "email": email,
        "full_name": full_name,
        "role": role,
        "created_at": datetime.now(),
        "is_active": True,
        "avatar_url": avatar_url
    }

    mock_users_db[user_id] = user
    return user


def create_mock_course(
        title: str,
        description: str,
        code: str,
        created_by_id: int,
        assigned_manager_id: Optional[int] = None,
        status: CourseStatus = CourseStatus.DRAFT,
        image_url: Optional[str] = None,
        short_description: Optional[str] = None,
        duration_hours: int = 0,
        tags: List[str] = None,
        requirements: List[str] = None,
        what_you_learn: List[str] = None,
        enrollment_status: str = "available"  # Новое поле: available, coming_soon, limited
) -> Dict:
    """Создать мок-курс"""
    global course_id_counter, mock_courses_db

    course_id = course_id_counter
    course_id_counter += 1

    now = datetime.now()
    course = {
        "id": course_id,
        "title": title,
        "description": description,
        "code": code,
        "status": status,
        "image_url": image_url,
        "default_image_url": "/static/default_course_image.jpg",
        "short_description": short_description,
        "duration_hours": duration_hours,
        "created_by_id": created_by_id,
        "assigned_manager_id": assigned_manager_id,
        "created_at": now,
        "updated_at": now,
        "tags": tags or [],
        "requirements": requirements or [],
        "what_you_learn": what_you_learn or [],
        "enrollment_status": enrollment_status  # Добавляем поле статуса записи
    }

    mock_courses_db[course_id] = course
    return course


def create_mock_module(
        course_id: int,
        title: str,
        description: Optional[str] = None,
        order: int = 0,
        is_published: bool = True
) -> Dict:
    """Создать мок-модуль"""
    global module_id_counter, mock_modules_db

    module_id = module_id_counter
    module_id_counter += 1

    module = {
        "id": module_id,
        "course_id": course_id,
        "title": title,
        "description": description,
        "order": order,
        "is_published": is_published,
        "created_at": datetime.now()
    }

    mock_modules_db[module_id] = module
    return module


def create_mock_lesson(
        module_id: int,
        title: str,
        content_type: ContentType,
        content_url: Optional[str] = None,
        content_text: Optional[str] = None,
        duration_minutes: int = 0,
        order: int = 0,
        lesson_type: LessonType = LessonType.THEORY,
        is_published: bool = True
) -> Dict:
    """Создать мок-урок"""
    global lesson_id_counter, mock_lessons_db

    lesson_id = lesson_id_counter
    lesson_id_counter += 1

    lesson = {
        "id": lesson_id,
        "module_id": module_id,
        "title": title,
        "content_type": content_type,
        "content_url": content_url,
        "content_text": content_text,
        "duration_minutes": duration_minutes,
        "order": order,
        "lesson_type": lesson_type,
        "is_published": is_published,
        "created_at": datetime.now()
    }

    mock_lessons_db[lesson_id] = lesson
    return lesson


def create_mock_test(
        module_id: int,
        title: str,
        description: Optional[str] = None,
        questions: List[Dict] = None,
        passing_score: int = 70,
        time_limit_minutes: Optional[int] = None,
        max_attempts: int = 3,
        is_published: bool = True
) -> Dict:
    """Создать мок-тест"""
    global test_id_counter, mock_tests_db

    test_id = test_id_counter
    test_id_counter += 1

    test = {
        "id": test_id,
        "module_id": module_id,
        "title": title,
        "description": description,
        "questions": questions or [],
        "passing_score": passing_score,
        "time_limit_minutes": time_limit_minutes,
        "max_attempts": max_attempts,
        "is_published": is_published,
        "created_at": datetime.now()
    }

    mock_tests_db[test_id] = test
    return test


def create_mock_enrollment(
        user_id: int,
        course_id: int,
        progress_percentage: float = 0.0
) -> Dict:
    """Создать мок-запись на курс"""
    global enrollment_id_counter, mock_enrollments_db

    enrollment_id = enrollment_id_counter
    enrollment_id_counter += 1

    now = datetime.now()
    enrollment = {
        "id": enrollment_id,
        "user_id": user_id,
        "course_id": course_id,
        "enrolled_at": now,
        "progress_percentage": progress_percentage,
        "current_lesson_id": None,
        "completed_at": None,
        "last_accessed": now,
        "is_active": True
    }

    mock_enrollments_db[enrollment_id] = enrollment
    return enrollment


def create_mock_progress(
        enrollment_id: int,
        lesson_id: int,
        is_completed: bool = False,
        time_spent_minutes: int = 0
) -> Dict:
    """Создать мок-прогресс урока"""
    global progress_id_counter, mock_progress_db

    progress_id = progress_id_counter
    progress_id_counter += 1

    now = datetime.now()
    progress = {
        "id": progress_id,
        "enrollment_id": enrollment_id,
        "lesson_id": lesson_id,
        "is_completed": is_completed,
        "completed_at": now if is_completed else None,
        "time_spent_minutes": time_spent_minutes,
        "last_accessed": now
    }

    mock_progress_db[progress_id] = progress
    return progress


# --- Функции для получения данных ---

def get_mock_user(user_id: int) -> Optional[Dict]:
    """Получить пользователя по ID"""
    return mock_users_db.get(user_id)


def get_mock_course(course_id: int) -> Optional[Dict]:
    """Получить курс по ID"""
    return mock_courses_db.get(course_id)


def get_mock_courses(
        status: Optional[CourseStatus] = None,
        limit: int = 20,
        offset: int = 0,
        search: Optional[str] = None
) -> List[Dict]:
    """Получить список курсов с фильтрацией"""
    courses = list(mock_courses_db.values())

    if status:
        courses = [c for c in courses if c["status"] == status]

    if search:
        search_lower = search.lower()
        courses = [
            c for c in courses
            if search_lower in c["title"].lower() or
               (c["description"] and search_lower in c["description"].lower())
        ]

    # Сортировка по дате создания (новые первыми)
    courses.sort(key=lambda x: x["created_at"], reverse=True)

    return courses[offset:offset + limit]


def get_mock_modules_by_course(course_id: int) -> List[Dict]:
    """Получить модули курса"""
    return [
        m for m in mock_modules_db.values()
        if m["course_id"] == course_id and m["is_published"]
    ]


def get_mock_lessons_by_module(module_id: int) -> List[Dict]:
    """Получить уроки модуля"""
    return [
        l for l in mock_lessons_db.values()
        if l["module_id"] == module_id and l["is_published"]
    ]


def get_mock_enrollment(user_id: int, course_id: int) -> Optional[Dict]:
    """Получить запись пользователя на курс"""
    for enrollment in mock_enrollments_db.values():
        if enrollment["user_id"] == user_id and enrollment["course_id"] == course_id:
            return enrollment
    return None


def get_mock_course_stats(course_id: int) -> Dict:
    """Получить статистику курса"""
    enrollments = [
        e for e in mock_enrollments_db.values()
        if e["course_id"] == course_id and e["is_active"]
    ]

    return {
        "enrollment_count": len(enrollments),
        "average_progress": sum(e["mprogress_percentage"] for e in enrollments) / len(enrollments) if enrollments else 0,
        "completion_count": len([e for e in enrollments if e["progress_percentage"] == 100])
    }


# Инициализируем данные при импорте
init_mock_data()