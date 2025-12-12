# repositories/mock/user_repository.py
import json
import os
from typing import Optional, List, Dict, Any

from core.security import hash_password
from core.roles import UserRole

DATA_FILE = "db/users.json"
os.makedirs("db", exist_ok=True)

if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump([], f, ensure_ascii=False, indent=2)


def _load_users() -> List[Dict]:
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return []


def _save_users(users: List[Dict]):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, ensure_ascii=False, indent=2)


class UserRepository:

    def get_all(self) -> List[Dict]:
        return _load_users()

    def get_by_login(self, login: str) -> Optional[Dict]:
        return next((u for u in _load_users() if u.get("login") == login), None)

    def get_by_email(self, email: str) -> Optional[Dict]:
        return next((u for u in _load_users() if u.get("email") == email), None)

    def get_by_id(self, user_id: int) -> Optional[Dict]:
        return next((u for u in _load_users() if u.get("id") == user_id), None)

    def create_user(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        users = _load_users()

        raw_password = user_data.pop("password")
        user_data.pop("password_confirm", None)
        user_data["hashed_password"] = hash_password(raw_password)

        # Роль: Enum → строка
        role = user_data.get("role")
        if role is not None and hasattr(role, "value"):
            user_data["role"] = role.value

        # Поля по умолчанию (БЕЗ РОЛИ!)
        defaults = {
            "company_id": None,
            "department_id": None,
            "position_id": None,
            "birth_date": None,
            "development_plan_id": None,
            "group_ids": [],
            "program_ids": [],
            "first_name": "",
            "last_name": "",
            "last_login_at": None,
            "rating": 0,
        }
        for k, v in defaults.items():
            user_data.setdefault(k, v)

        if user_data.get("birth_date") is not None:
            user_data["birth_date"] = str(user_data["birth_date"])

        user_data["id"] = max((u.get("id", 0) for u in users), default=0) + 1

        users.append(user_data)
        _save_users(users)
        return user_data
    def update_user(self, user_id: int, update_data: Dict[str, Any]) -> Optional[Dict]:
        users = _load_users()
        updated_user = None

        for user in users:
            if user["id"] == user_id:

                # пароль
                if "password" in update_data and update_data["password"]:
                    raw_password = update_data.pop("password")
                    update_data.pop("password_confirm", None)
                    user["hashed_password"] = hash_password(raw_password)

                # роль Enum → строка
                if "role" in update_data:
                    role = update_data["role"]
                    if hasattr(role, "value"):
                        update_data["role"] = role.value

                # дата рождения
                if "birth_date" in update_data and update_data["birth_date"] is not None:
                    update_data["birth_date"] = str(update_data["birth_date"])

                # обновление остальных полей
                for k, v in update_data.items():
                    user[k] = v

                updated_user = user
                break

        if not updated_user:
            return None

        _save_users(users)
        return updated_user

    def delete_user(self, user_id: int) -> bool:
        users = _load_users()
        new_users = [u for u in users if u["id"] != user_id]
        if len(new_users) == len(users):
            return False
        _save_users(new_users)
        return True
    def update_last_login(self, user_id: int) -> Optional[Dict]:
        from datetime import datetime

        users = _load_users()
        for user in users:
            if user["id"] == user_id:
                user["last_login_at"] = datetime.now().isoformat()
                _save_users(users)
                return user
        return None


user_repository = UserRepository()
