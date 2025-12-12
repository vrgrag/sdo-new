from enum import Enum
class CourseStatus(str, Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"


class ContentType(str, Enum):
    VIDEO = "video"
    PDF = "pdf"
    DOCX = "docx"
    PPTX = "pptx"
    TEXT = "text"
    IMAGE = "image"


class LessonType(str, Enum):
    THEORY = "theory"
    PRACTICE = "practice"
    TEST = "test"