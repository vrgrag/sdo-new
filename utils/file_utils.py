# utils/file_utils.py
import os
from pathlib import Path
from typing import Optional

# Маппинг расширений файлов к категориям
FILE_CATEGORIES = {
    "photos": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp", ".svg"],
    "videos": [".mp4", ".avi", ".mov", ".wmv", ".flv", ".webm", ".mkv"],
    "pdfs": [".pdf"],
    "docs": [".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx", ".txt", ".rtf", ".odt"],
    "audio": [".mp3", ".wav", ".ogg", ".flac", ".aac", ".m4a"],
    "other": []  # Все остальное
}


def get_file_category(filename: str) -> str:
    """
    Определяет категорию файла по его расширению.
    Возвращает название подпапки (photos, videos, pdfs, docs, audio, other)
    """
    ext = Path(filename).suffix.lower()
    
    for category, extensions in FILE_CATEGORIES.items():
        if ext in extensions:
            return category
    
    return "other"


def get_uploads_path(category: Optional[str] = None, filename: Optional[str] = None) -> str:
    """
    Возвращает путь к файлу в папке uploads.
    Если указана категория, файл будет в соответствующей подпапке.
    Если категория не указана, но указан filename, категория определяется автоматически.
    """
    base_path = "uploads"
    
    if filename and not category:
        category = get_file_category(filename)
    
    if category:
        return os.path.join(base_path, category, filename) if filename else os.path.join(base_path, category)
    
    return os.path.join(base_path, filename) if filename else base_path


def ensure_upload_dir(category: Optional[str] = None) -> str:
    """
    Создает директорию для загрузки файлов и возвращает путь к ней.
    """
    path = get_uploads_path(category=category)
    os.makedirs(path, exist_ok=True)
    return path

