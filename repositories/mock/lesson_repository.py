# repositories/mock/lesson_repository.py
from typing import List, Optional
from schemas import LessonResponse, LessonCreate
from repositories.base import ILessonRepository  # ← создадим ниже
from .mock_data import get_lessons_by_module, MOCK_LESSONS


class MockLessonRepository(ILessonRepository):
    def get_all(
            self,
            module_id: Optional[int] = None,
            lesson_type: Optional[str] = None
    ) -> List[LessonResponse]:
        lessons = MOCK_LESSONS.copy()

        if module_id is not None:
            lessons = [l for l in lessons if l["module_id"] == module_id]

        if lesson_type is not None:
            lessons = [l for l in lessons if l["lesson_type"] == lesson_type]

        # Сортировка по module_id, затем по order
        lessons.sort(key=lambda x: (x["module_id"], x["order"]))
        return [self._dict_to_response(l) for l in lessons]

    def get_by_id(self, lesson_id: int) -> Optional[LessonResponse]:
        for lesson in MOCK_LESSONS:
            if lesson["id"] == lesson_id:
                return self._dict_to_response(lesson)
        return None

    def get_by_module(self, module_id: int) -> List[LessonResponse]:
        """Вернуть все уроки для указанного модуля."""
        lessons = get_lessons_by_module(module_id)
        # сортировка по order
        lessons.sort(key=lambda x: x["order"])
        return [self._dict_to_response(l) for l in lessons]

    def _dict_to_response(self, lesson_dict: dict) -> LessonResponse:
        data = lesson_dict.copy()
        for key in list(data.keys()):
            if key not in LessonResponse.model_fields:
                data.pop(key, None)
        return LessonResponse(**data)
