import os
from dotenv import load_dotenv
import socket

load_dotenv('../.env')

POSTGRES_USER = os.getenv("POSTGRES_USER", "admin")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "1234")
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")
POSTGRES_DB = os.getenv("POSTGRES_DB", "postgres")
DATABASE_URL=(f'postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}/{POSTGRES_DB}')

def get_ip_address() -> str:
    """Определяет локальный IP-адрес (для dev)"""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('10.255.255.255', 1))
        return s.getsockname()[0]
    except Exception:
        return '127.0.0.1'
    finally:
        s.close()


class Settings:
    # Хост и порт для запуска uvicorn
    SERVER_HOST: str = os.getenv("SERVER_HOST", "0.0.0.0")
    SERVER_PORT: int = int(os.getenv("SERVER_PORT", "8001"))
    # IP для фронта (всегда автоопределяем)
    SERVER_IP: str = get_ip_address()
    # URL для фронта
    SERVER_URL: str = f"http://{SERVER_IP}:{SERVER_PORT}/api"
    # URL для внутреннего запуска (например, health-check)
    SERVER_INTERNAL_URL: str = f"http://{SERVER_HOST}:{SERVER_PORT}"
    # Пути для статики
    STATIC_URL: str = "/static"
    UPLOADS_URL: str = "/uploads"
#  JWT НАСТРОЙКИ
    SECRET_KEY: str = os.getenv("SECRET_KEY", "change-me-in-production-1234567890")
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 часа (можно 30 минут)

    # Это нужно для BaseSettings, чтобы он читал .env
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
settings = Settings()
