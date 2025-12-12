from typing import List, Optional
from schemas import ModuleResponse
from repositories.base import IModuleRepository
from .mock_data import MOCK_MODULES



class MockModuleRepository(IModuleRepository):
    def get_by_course(self, course_id: int) -> List[ModuleResponse]:
        modules = [m for m in MOCK_MODULES if m["course_id"] == course_id and m["is_published"]]
        modules.sort(key=lambda x: x["order"])
        return [self._dict_to_response(m) for m in modules]

    def get_by_id(self, module_id: int) -> Optional[ModuleResponse]:
        for module in MOCK_MODULES:
            if module["id"] == module_id:
                return self._dict_to_response(module)
        return None

    def _dict_to_response(self, module_dict: dict) -> ModuleResponse:
        data = module_dict.copy()
        for key in list(data.keys()):
            if key not in ModuleResponse.model_fields:
                data.pop(key, None)
        return ModuleResponse(**data)