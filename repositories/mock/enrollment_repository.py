# repositories/mock/enrollment_repository.py
import json
import os
from typing import List, Dict

DATA_FILE = "db/enrollments.json"

os.makedirs("db", exist_ok=True)
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        # новая структура по умолчанию
        json.dump({"students": {}, "trainers": {}}, f, ensure_ascii=False, indent=2)


def _load() -> Dict:
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError:
        data = {"students": {}, "trainers": {}}

    if "trainers" not in data:
        data["trainers"] = {}

    if "teachers" in data and isinstance(data["teachers"], dict):
        # объединяем, не теряя данные
        for uid, course_ids in data["teachers"].items():
            data["trainers"].setdefault(uid, [])
            for cid in course_ids or []:
                if cid not in data["trainers"][uid]:
                    data["trainers"][uid].append(cid)

    if "students" not in data:
        data["students"] = {}

    return data


def _save(data: Dict) -> None:
    # сохраняем только новое имя ключа
    data.pop("teachers", None)
    data.setdefault("students", {})
    data.setdefault("trainers", {})

    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


class EnrollmentRepository:


    def enroll_student(self, student_id: int, course_id: int) -> None:
        data = _load()
        key = str(student_id)
        data.setdefault("students", {})
        data["students"].setdefault(key, [])
        if course_id not in data["students"][key]:
            data["students"][key].append(course_id)
        _save(data)

    def unenroll_student(self, student_id: int, course_id: int) -> None:
        data = _load()
        key = str(student_id)
        if key in data.get("students", {}):
            data["students"][key] = [cid for cid in data["students"][key] if cid != course_id]
            _save(data)

    def get_courses_for_student(self, student_id: int) -> List[int]:
        data = _load()
        return data.get("students", {}).get(str(student_id), [])

    def assign_trainer(self, trainer_id: int, course_id: int) -> None:
        data = _load()
        key = str(trainer_id)
        data.setdefault("trainers", {})
        data["trainers"].setdefault(key, [])
        if course_id not in data["trainers"][key]:
            data["trainers"][key].append(course_id)
        _save(data)

    def unassign_trainer(self, trainer_id: int, course_id: int) -> None:
        data = _load()
        key = str(trainer_id)
        if key in data.get("trainers", {}):
            data["trainers"][key] = [cid for cid in data["trainers"][key] if cid != course_id]
            _save(data)

    def get_courses_for_trainer(self, trainer_id: int) -> List[int]:
        data = _load()
        return data.get("trainers", {}).get(str(trainer_id), [])
    def assign_teacher(self, teacher_id: int, course_id: int) -> None:
        return self.assign_trainer(teacher_id, course_id)

    def unassign_teacher(self, teacher_id: int, course_id: int) -> None:
        return self.unassign_trainer(teacher_id, course_id)

    def get_courses_for_teacher(self, teacher_id: int) -> List[int]:
        return self.get_courses_for_trainer(teacher_id)
