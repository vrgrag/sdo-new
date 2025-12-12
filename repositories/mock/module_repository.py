import json
import os
from typing import List, Optional

from repositories.base import IModuleRepository
from schemas import ModuleResponse, ModuleCreate, ModuleUpdate

DATA_FILE = "db/modules.json"
os.makedirs("db", exist_ok=True)


def _load() -> list[dict]:
    if not os.path.exists(DATA_FILE):
        return []
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return []


def _save(data: list[dict]) -> None:
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


class JsonModuleRepository(IModuleRepository):
    def get_by_course(self, course_id: int) -> List[ModuleResponse]:
        modules = [m for m in _load() if m.get("course_id") == course_id]
        modules.sort(key=lambda x: x.get("order", 0))
        return [ModuleResponse(**m) for m in modules]

    def get_by_id(self, module_id: int) -> Optional[ModuleResponse]:
        for m in _load():
            if m.get("id") == module_id:
                return ModuleResponse(**m)
        return None

    # Если твой IModuleRepository не требует create/update/delete — можешь удалить эти методы.
    def create(self, module_data: ModuleCreate) -> ModuleResponse:
        modules = _load()
        new_id = max([m.get("id", 0) for m in modules], default=0) + 1
        module = {"id": new_id, **module_data.model_dump()}
        modules.append(module)
        _save(modules)
        return ModuleResponse(**module)

    def update(self, module_id: int, module_data: ModuleUpdate) -> Optional[ModuleResponse]:
        modules = _load()
        payload = module_data.model_dump(exclude_unset=True)

        for m in modules:
            if m.get("id") == module_id:
                m.update(payload)
                _save(modules)
                return ModuleResponse(**m)

        return None

    def delete(self, module_id: int) -> bool:
        modules = _load()
        new_modules = [m for m in modules if m.get("id") != module_id]
        if len(new_modules) == len(modules):
            return False
        _save(new_modules)
        return True
