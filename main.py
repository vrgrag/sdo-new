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


app.mount(settings.STATIC_URL, StaticFiles(directory="static"), name="static")
print(settings.UPLOADS_URL, "<<<<<<<<<<<<< MY UPLOADS URL")
app.mount(settings.UPLOADS_URL, StaticFiles(directory="/home/vrgrag/sdo-new/uploads"), name="uploads")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


app.include_router(courses_router, tags=["Courses"])
app.include_router(lessons_router, tags=["Lessons"])
app.include_router(auth_router)
app.include_router(events_router)
app.include_router(users_router)
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
