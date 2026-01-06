import os
from dotenv import load_dotenv
import socket
from sqlalchemy.ext.asyncio import create_async_engine

load_dotenv('env')


POSTGRES_USER = os.getenv("POSTGRES_USER", "admin")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "1234")
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")
POSTGRES_DB = os.getenv("POSTGRES_DB", "postgres")

DATABASE_URL_ASYNC = os.getenv(
    "DATABASE_URL_ASYNC",
    f"postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}",
)

DATABASE_URL_SYNC = os.getenv(
    "DATABASE_URL_SYNC",
    f"postgresql+psycopg2://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}",
)

def get_ip_address() -> str:
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('10.255.255.255', 1))
        return s.getsockname()[0]
    except Exception:
        return '127.0.0.1'
    finally:
        s.close()


class Settings:
    SERVER_HOST: str = os.getenv("SERVER_HOST", "0.0.0.0")
    SERVER_PORT: int = int(os.getenv("SERVER_PORT", "8001"))
    SERVER_IP: str = get_ip_address()

    STATIC_URL: str = "/static"
    UPLOADS_URL: str = "/uploads"

    SECRET_KEY: str = os.getenv("SECRET_KEY", "change-me-in-production-1234567890")
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24

class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
settings = Settings()
settings.SERVER_URL = f"http://{settings.SERVER_IP}:{settings.SERVER_PORT}/api"
settings.SERVER_INTERNAL_URL = f"http://{settings.SERVER_HOST}:{settings.SERVER_PORT}"
