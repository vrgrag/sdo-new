# 📁 api/v1/__init__.py
from fastapi import APIRouter
from .courses import router as courses_router

router = APIRouter(prefix="/api/v1")

router.include_router(courses_router, prefix="/courses", tags=["courses"])

# Или просто
# router.include_router(courses_router)