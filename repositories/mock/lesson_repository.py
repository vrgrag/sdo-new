import json
import os
from typing import List, Optional

from repositories.base import ILessonRepository
from schemas import LessonResponse, LessonCreate, LessonUpdate

DATA_FILE = "db/lessons.json"
os.makedirs("db", exist_ok=True)


def _load() -> list[dict]:
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def _save(data: list[dict]):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


class JsonLessonRepository(ILessonRepository):

    def get_all(
        self,
        module_id: Optional[int] = None,
        lesson_type: Optional[str] = None
    ) -> List[LessonResponse]:
        lessons = _load()

        if module_id is not None:
            lessons = [l for l in lessons if l["module_id"] == module_id]

        if lesson_type is not None:
            lessons = [l for l in lessons if l["lesson_type"] == lesson_type]

        lessons.sort(key=lambda x: (x["module_id"], x["order"]))
        return [LessonResponse(**l) for l in lessons]

    def get_by_id(self, lesson_id: int) -> Optional[LessonResponse]:
        for l in _load():
            if l["id"] == lesson_id:
                return LessonResponse(**l)
        return None

    def get_by_module(self, module_id: int) -> List[LessonResponse]:
        lessons = _load()
        lessons = [l for l in lessons if l.get("module_id") == module_id]
        lessons.sort(key=lambda x: x.get("order", 0))
        return [LessonResponse(**l) for l in lessons]

    def create(self, lesson: LessonCreate) -> LessonResponse:
        lessons = _load()
        new_id = max([l["id"] for l in lessons], default=0) + 1

        new_lesson = {
            "id": new_id,
            **lesson.model_dump()
        }

        lessons.append(new_lesson)
        _save(lessons)
        return LessonResponse(**new_lesson)

    def update(
        self,
        lesson_id: int,
        lesson_data: LessonUpdate
    ) -> Optional[LessonResponse]:
        lessons = _load()

        for l in lessons:
            if l["id"] == lesson_id:
                for k, v in lesson_data.model_dump(exclude_unset=True).items():
                    l[k] = v
                _save(lessons)
                return LessonResponse(**l)

        return None

    def delete(self, lesson_id: int) -> bool:
        lessons = _load()
        new_lessons = [l for l in lessons if l["id"] != lesson_id]

        if len(new_lessons) == len(lessons):
            return False

        _save(new_lessons)
        return True
