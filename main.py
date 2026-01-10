import os
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.security import OAuth2PasswordBearer
from core.config import settings

from api.v1.courses import router as courses_router
from api.v1.lessons import router as lessons_router
from api.v1.events import router as events_router
from api.v1.users import router as users_router
from api.v1.auth import router as auth_router
from api.v1.companies import router as companies_router
from api.v1.departments import router as departments_router
from api.v1.positions import router as positions_router
from api.v1.tests import router as tests_router
from api.v1.questions import router as questions_router
from api.v1.answers import router as answers_router
from api.v1.user_answers import router as user_answers_router
from api.v1.tasks import router as tasks_router
from api.v1.materials import router as materials_router
from core.db import Base, engine

app = FastAPI(
    title="Course Platform API",
    version="1.0.0",
    description="Backend для образовательной платформы (курсы, модули, уроки)",
    root_path="/api",
)


FRONTEND_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:5173",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:5173",
    f"http://{settings.SERVER_IP}:3000",
    f"http://{settings.SERVER_IP}:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=FRONTEND_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


for dir_name in ["static", "uploads"]:
    os.makedirs(dir_name, exist_ok=True)

# Создаем структуру подпапок для uploads
uploads_subdirs = ["docs", "photos", "videos", "pdfs", "audio", "other"]
for subdir in uploads_subdirs:
    uploads_subdir_path = os.path.join("uploads", subdir)
    os.makedirs(uploads_subdir_path, exist_ok=True)

app.mount(settings.STATIC_URL, StaticFiles(directory="static"), name="static")
print(settings.UPLOADS_URL, "<<<<<<<<<<<<< MY UPLOADS URL")
app.mount(settings.UPLOADS_URL, StaticFiles(directory="/home/vrgrag/sdo-new/uploads"), name="uploads")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

@app.on_event("startup")
async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)



app.include_router(courses_router, tags=["Courses"])
app.include_router(lessons_router, tags=["Lessons"])
app.include_router(auth_router)
app.include_router(events_router)
app.include_router(users_router)
app.include_router(companies_router)
app.include_router(departments_router)
app.include_router(positions_router)
app.include_router(tests_router, tags=["Tests"])
app.include_router(questions_router, tags=["Questions"])
app.include_router(answers_router, tags=["Answers"])
app.include_router(user_answers_router, tags=["UserAnswers"])
app.include_router(tasks_router, tags=["Tasks"])
app.include_router(materials_router, tags=["Materials"])
@app.get("/", include_in_schema=False)
async def root():
    return {
        "message": "Course Platform API работает!",
        "server": {
            "ip": settings.SERVER_IP,
            "port": settings.SERVER_PORT,
            "url": settings.SERVER_URL
        },
        "docs": f"{settings.SERVER_URL}/docs",
        "redoc": f"{settings.SERVER_URL}/redoc"
    }


@app.get("/health", include_in_schema=False)
async def health_check():
    return {
        "status": "healthy",
        "server_ip": settings.SERVER_IP,
        "server_port": settings.SERVER_PORT,
        "server_url": settings.SERVER_URL
    }


if __name__ == "__main__":
    print("=" * 60)
    print("🌐 API ДОСТУПНО ПО АДРЕСУ:")
    print(f"   {settings.SERVER_URL}")
    print()
    print("📚 ДОКУМЕНТАЦИЯ:")
    print(f"   Swagger UI: {settings.SERVER_URL}/docs")
    print(f"   ReDoc:      {settings.SERVER_URL}/redoc")
    print("=" * 60)

    uvicorn.run(
        "main:app",
        host=settings.SERVER_HOST,
        port=settings.SERVER_PORT,
        reload=True,
        log_level="info"
    )
