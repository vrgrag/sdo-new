from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from enum import Enum

import socket
from mock_data import (
    get_mock_courses,
    get_mock_course,
    get_mock_modules_by_course,
    get_mock_lessons_by_module,
    get_mock_enrollment,
    CourseStatus,
    ContentType,
    LessonType
)



# Получаем IP адрес машины
def get_ip_address():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP


SERVER_IP = get_ip_address()
SERVER_PORT = 8000
SERVER_URL = f"http://{SERVER_IP}:{SERVER_PORT}"

print(f"Сервер запущен по адресу: {SERVER_URL}")

# Создаем приложение
app = FastAPI(title="Course Platform API", version="1.0.0")

# ВАЖНО: Разрешаем CORS для фронтенда
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Модели данных
class ContentTypeEnum(str, Enum):
    VIDEO = "video"
    PDF = "pdf"
    TEXT = "text"
    PRESENTATION = "presentation"


class LessonTypeEnum(str, Enum):
    THEORY = "theory"
    PRACTICE = "practice"
    TEST = "test"


class LessonResponse(BaseModel):
    id: int
    title: str
    content_type: ContentTypeEnum
    content_url: Optional[str] = None
    content_text: Optional[str] = None
    duration_minutes: int
    order: int
    lesson_type: LessonTypeEnum
    is_published: bool

    class Config:
        from_attributes = True


class ModuleResponse(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    order: int
    is_published: bool
    lessons: List[LessonResponse] = []

    class Config:
        from_attributes = True


class CourseResponse(BaseModel):
    id: int
    title: str
    description: str
    status: CourseStatus
    image_url: Optional[str] = None
    short_description: Optional[str] = None
    duration_hours: Optional[int] = 0
    tags: List[str] = []
    requirements: List[str] = []
    what_you_learn: List[str] = []

    class Config:
        from_attributes = True


class CourseDetailResponse(CourseResponse):
    modules: List[ModuleResponse] = []
    enrollment_info: Optional[Dict[str, Any]] = None


class EnrollmentResponse(BaseModel):
    id: int
    user_id: int
    course_id: int
    enrolled_at: str
    progress_percentage: float
    current_lesson_id: Optional[int] = None
    is_active: bool


# Эндпоинты
@app.get("/")
async def root():
    return {
        "message": "Course Platform API работает!",
        "server_ip": SERVER_IP,
        "server_port": SERVER_PORT,
        "api_endpoints": {
            "courses": f"{SERVER_URL}/api/courses",
            "course_detail": f"{SERVER_URL}/api/courses/{{id}}",
            "course_modules": f"{SERVER_URL}/api/courses/{{id}}/modules",
            "course_content": f"{SERVER_URL}/api/courses/{{id}}/content",
            "health": f"{SERVER_URL}/api/health"
        }
    }


@app.get("/api/courses", response_model=List[CourseResponse])
async def get_courses():
    """Получить список всех курсов"""
    courses = get_mock_courses()

    response_courses = []
    for course in courses:
        image_url = course.get("image_url")
        if image_url and not image_url.startswith("http"):
            image_url = f"{SERVER_URL}{image_url}"

        response_courses.append({
            "id": course["id"],
            "title": course["title"],
            "description": course["description"],
            "status": course["status"],
            "image_url": image_url,
            "short_description": course.get("short_description"),
            "duration_hours": course.get("duration_hours", 0),
            "tags": course.get("tags", []),
            "requirements": course.get("requirements", []),
            "what_you_learn": course.get("what_you_learn", [])
        })

    return response_courses


@app.get("/api/courses/{course_id}", response_model=CourseDetailResponse)
async def get_course(course_id: int, user_id: Optional[int] = None):
    """Получить детальную информацию о курсе со структурой"""
    course = get_mock_course(course_id)

    if not course:
        raise HTTPException(status_code=404, detail="Курс не найден")

    # Формируем полный URL для изображения
    image_url = course.get("image_url")
    if image_url and not image_url.startswith("http"):
        image_url = f"{SERVER_URL}{image_url}"

    # Получаем модули курса
    modules = get_mock_modules_by_course(course_id)
    module_responses = []

    for module in modules:
        # Получаем уроки для каждого модуля
        lessons = get_mock_lessons_by_module(module["id"])

        lesson_responses = []
        for lesson in lessons:
            # Формируем полный URL для контента, если это внешняя ссылка
            content_url = lesson.get("content_url")
            if content_url and content_url.startswith("/static/"):
                content_url = f"{SERVER_URL}{content_url}"

            lesson_responses.append({
                "id": lesson["id"],
                "title": lesson["title"],
                "content_type": lesson["content_type"],
                "content_url": content_url,
                "content_text": lesson.get("content_text"),
                "duration_minutes": lesson.get("duration_minutes", 0),
                "order": lesson.get("order", 0),
                "lesson_type": lesson.get("lesson_type", LessonTypeEnum.THEORY),
                "is_published": lesson.get("is_published", True)
            })

        # Сортируем уроки по порядку
        lesson_responses.sort(key=lambda x: x["order"])

        module_responses.append({
            "id": module["id"],
            "title": module["title"],
            "description": module.get("description"),
            "order": module.get("order", 0),
            "is_published": module.get("is_published", True),
            "lessons": lesson_responses
        })

    # Сортируем модули по порядку
    module_responses.sort(key=lambda x: x["order"])

    # Получаем информацию о записи пользователя, если указан user_id
    enrollment_info = None
    if user_id:
        enrollment = get_mock_enrollment(user_id, course_id)
        if enrollment:
            enrollment_info = {
                "enrolled_at": enrollment["enrolled_at"].isoformat() if hasattr(enrollment["enrolled_at"],
                                                                                "isoformat") else str(
                    enrollment["enrolled_at"]),
                "progress_percentage": enrollment.get("progress_percentage", 0),
                "current_lesson_id": enrollment.get("current_lesson_id"),
                "is_active": enrollment.get("is_active", True)
            }

    return {
        "id": course["id"],
        "title": course["title"],
        "description": course["description"],
        "status": course["status"],
        "image_url": image_url,
        "short_description": course.get("short_description"),
        "duration_hours": course.get("duration_hours", 0),
        "tags": course.get("tags", []),
        "requirements": course.get("requirements", []),
        "what_you_learn": course.get("what_you_learn", []),
        "modules": module_responses,
        "enrollment_info": enrollment_info
    }


@app.get("/api/courses/{course_id}/modules", response_model=List[ModuleResponse])
async def get_course_modules(course_id: int):
    """Получить модули курса с уроками"""
    modules = get_mock_modules_by_course(course_id)

    if not modules:
        raise HTTPException(status_code=404, detail="Модули не найдены или курс не существует")

    module_responses = []
    for module in modules:
        lessons = get_mock_lessons_by_module(module["id"])

        lesson_responses = []
        for lesson in lessons:
            content_url = lesson.get("content_url")
            if content_url and content_url.startswith("/static/"):
                content_url = f"{SERVER_URL}{content_url}"

            lesson_responses.append({
                "id": lesson["id"],
                "title": lesson["title"],
                "content_type": lesson["content_type"],
                "content_url": content_url,
                "content_text": lesson.get("content_text"),
                "duration_minutes": lesson.get("duration_minutes", 0),
                "order": lesson.get("order", 0),
                "lesson_type": lesson.get("lesson_type", LessonTypeEnum.THEORY),
                "is_published": lesson.get("is_published", True)
            })

        lesson_responses.sort(key=lambda x: x["order"])

        module_responses.append({
            "id": module["id"],
            "title": module["title"],
            "description": module.get("description"),
            "order": module.get("order", 0),
            "is_published": module.get("is_published", True),
            "lessons": lesson_responses
        })

    module_responses.sort(key=lambda x: x["order"])
    return module_responses


@app.get("/api/courses/{course_id}/content")
async def get_course_content(course_id: int):
    """Получить полную структуру курса для отображения контента"""
    course = get_mock_course(course_id)

    if not course:
        raise HTTPException(status_code=404, detail="Курс не найден")

    # Получаем модули
    modules = get_mock_modules_by_course(course_id)

    course_structure = {
        "course": {
            "id": course["id"],
            "title": course["title"],
            "description": course["description"]
        },
        "modules": []
    }

    total_duration_minutes = 0
    total_lessons = 0

    for module in modules:
        lessons = get_mock_lessons_by_module(module["id"])

        module_duration = sum(lesson.get("duration_minutes", 0) for lesson in lessons)
        total_duration_minutes += module_duration
        total_lessons += len(lessons)

        module_data = {
            "id": module["id"],
            "title": module["title"],
            "description": module.get("description"),
            "order": module.get("order", 0),
            "duration_minutes": module_duration,
            "lessons_count": len(lessons),
            "lessons": []
        }

        for lesson in lessons:
            content_url = lesson.get("content_url")
            if content_url and content_url.startswith("/static/"):
                content_url = f"{SERVER_URL}{content_url}"

            module_data["lessons"].append({
                "id": lesson["id"],
                "title": lesson["title"],
                "content_type": lesson["content_type"],
                "content_url": content_url,
                "content_text": lesson.get("content_text"),
                "duration_minutes": lesson.get("duration_minutes", 0),
                "order": lesson.get("order", 0),
                "lesson_type": lesson.get("lesson_type", "theory"),
                "is_published": lesson.get("is_published", True)
            })

        module_data["lessons"].sort(key=lambda x: x["order"])
        course_structure["modules"].append(module_data)

    course_structure["modules"].sort(key=lambda x: x["order"])
    course_structure["summary"] = {
        "total_modules": len(modules),
        "total_lessons": total_lessons,
        "total_duration_minutes": total_duration_minutes,
        "total_duration_hours": round(total_duration_minutes / 60, 1)
    }

    return course_structure


@app.get("/api/lessons/{lesson_id}")
async def get_lesson(lesson_id: int):
    """Получить детальную информацию об уроке"""
    from mock_data import mock_lessons_db

    lesson = mock_lessons_db.get(lesson_id)

    if not lesson:
        raise HTTPException(status_code=404, detail="Урок не найден")

    # Формируем полный URL для контента
    content_url = lesson.get("content_url")
    if content_url and content_url.startswith("/static/"):
        content_url = f"{SERVER_URL}{content_url}"

    return {
        "id": lesson["id"],
        "title": lesson["title"],
        "content_type": lesson["content_type"],
        "content_url": content_url,
        "content_text": lesson.get("content_text"),
        "duration_minutes": lesson.get("duration_minutes", 0),
        "order": lesson.get("order", 0),
        "lesson_type": lesson.get("lesson_type", "theory"),
        "is_published": lesson.get("is_published", True)
    }


@app.get("/api/health")
async def health_check():
    return {
        "status": "healthy",
        "server": SERVER_IP,
        "port": SERVER_PORT,
        "access_url": SERVER_URL,
        "endpoints": [
            "/api/courses",
            "/api/courses/{id}",
            "/api/courses/{id}/modules",
            "/api/courses/{id}/content",
            "/api/lessons/{id}"
        ]
    }

from fastapi import UploadFile, File

@app.post("/api/upload")
async def upload_file(file: UploadFile = File(...), category: Optional[str] = "documents"):
    """Загрузить файл и сохранить в нужную папку"""
    # Категория определяет папку: documents, pdfs, videos
    valid_categories = ["documents", "pdfs", "videos", "temp"]
    if category not in valid_categories:
        raise HTTPException(status_code=400, detail="Неверная категория")

    save_dir = os.path.join("uploads", category)
    os.makedirs(save_dir, exist_ok=True)

    file_path = os.path.join(save_dir, file.filename)
    with open(file_path, "wb") as f:
        f.write(await file.read())

    # Формируем URL для фронта
    file_url = f"{SERVER_URL}/uploads/{category}/{file.filename}"

    return {
        "filename": file.filename,
        "category": category,
        "url": file_url,
        "content_type": file.content_type
    }

# Поддержка статических файлов
from fastapi.staticfiles import StaticFiles
import os

static_dir = "static"
if not os.path.exists(static_dir):
    os.makedirs(static_dir)
    print(f"Создана папка для статических файлов: {static_dir}")

app.mount("/static", StaticFiles(directory=static_dir), name="static")
uploads_dir = "uploads"
if not os.path.exists(uploads_dir):
    os.makedirs(uploads_dir)
    print(f"Создана папка для загрузок: {uploads_dir}")

app.mount("/uploads", StaticFiles(directory=uploads_dir), name="uploads")

# Запуск
if __name__ == "__main__":
    import uvicorn

    print("=" * 50)
    print("API ЭНДПОИНТЫ ДЛЯ РАБОТЫ С КУРСАМИ:")
    print("=" * 50)
    print(f"1. Список курсов: {SERVER_URL}/api/courses")
    print(f"2. Детали курса (со структурой): {SERVER_URL}/api/courses/1")
    print(f"3. Модули курса: {SERVER_URL}/api/courses/1/modules")
    print(f"4. Полная структура курса: {SERVER_URL}/api/courses/1/content")
    print(f"5. Детали урока: {SERVER_URL}/api/lessons/1")
    print("=" * 50)
    print(f"IP адрес: {SERVER_IP}")
    print(f"Порт: {SERVER_PORT}")
    print("=" * 50)

    uvicorn.run(app="main_network:app", host="0.0.0.0", port=SERVER_PORT, reload=True)