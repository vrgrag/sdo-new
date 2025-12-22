# repositories/db/user_repository.py
from typing import Optional, List, Dict, Any
from datetime import datetime

from sqlalchemy.orm import Session

from core.security import hash_password
from db_models.users import Users


def _to_dict(user: Users) -> Dict[str, Any]:
    # Формат похожий на твой JSON, чтобы остальной код не падал
    return {
        "id": user.id,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "middle_name": user.middle_name,
        "email": user.email,
        "birth_date": user.birth_date.isoformat() if user.birth_date else None,
        "is_active": user.is_active,
        "created_at": user.created_at.isoformat() if user.created_at else None,
        "last_login_at": user.last_login.isoformat() if user.last_login else None,  # совместимость
        "company_id": user.company_id,
        "department_id": user.department_id,
        "position_id": user.position_id,
        "role_id": user.role_id,
        "hire_date": user.hire_date.isoformat() if user.hire_date else None,
        "telegram_username": user.telegram_username,
    }


class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self) -> List[Dict]:
        users = self.db.query(Users).order_by(Users.id.asc()).all()
        return [_to_dict(u) for u in users]

    def get_by_login(self, login: str) -> Optional[Dict]:
        # В БД нет поля login (по твоему выводу). Обычно login = email или telegram_username.
        # Я делаю логин как email.
        user = self.db.query(Users).filter(Users.email == login).first()
        return _to_dict(user) if user else None

    def get_by_email(self, email: str) -> Optional[Dict]:
        user = self.db.query(Users).filter(Users.email == email).first()
        return _to_dict(user) if user else None

    def get_by_id(self, user_id: int) -> Optional[Dict]:
        user = self.db.query(Users).filter(Users.id == user_id).first()
        return _to_dict(user) if user else None

    def create_user(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        if "login" in user_data and "email" not in user_data:
            user_data["email"] = user_data["login"]
        raw_password = user_data.pop("password")
        user_data.pop("password_confirm", None)

        # совместимость со старым кодом: role мог быть enum/строкой
        role_id = user_data.get("role_id")
        if role_id is None and "role" in user_data:
            role = user_data["role"]
            # если прилетает Enum, берем value
            if hasattr(role, "value"):
                role = role.value
            # если раньше role был строкой, а в БД role_id — это int,
            # тут нельзя угадать маппинг без таблицы roles.
            # поэтому просто не трогаем, если не int.
            if isinstance(role, int):
                role_id = role

        birth_date = user_data.get("birth_date")
        if isinstance(birth_date, str):
            # если прилетает ISO строка
            try:
                birth_date = datetime.fromisoformat(birth_date)
            except ValueError:
                birth_date = None

        now = datetime.now().astimezone()

        user = Users(
            first_name=user_data.get("first_name") or "",
            last_name=user_data.get("last_name") or "",
            middle_name=user_data.get("middle_name"),
            email=user_data["email"],
            password_hash=hash_password(raw_password),
            created_at=user_data.get("created_at") or now,
            is_active=user_data.get("is_active"),
            birth_date=birth_date,
            company_id=user_data.get("company_id"),
            department_id=user_data.get("department_id"),
            position_id=user_data.get("position_id"),
            role_id=role_id,
            hire_date=user_data.get("hire_date"),
            telegram_username=user_data.get("telegram_username"),
        )

        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return _to_dict(user)

    def update_user(self, user_id: int, update_data: Dict[str, Any]) -> Optional[Dict]:
        user = self.db.query(Users).filter(Users.id == user_id).first()
        if not user:
            return None

        # пароль
        if update_data.get("password"):
            raw_password = update_data.pop("password")
            update_data.pop("password_confirm", None)
            user.password_hash = hash_password(raw_password)

        # birth_date
        if "birth_date" in update_data:
            bd = update_data["birth_date"]
            if isinstance(bd, str):
                try:
                    bd = datetime.fromisoformat(bd)
                except ValueError:
                    bd = None
            user.birth_date = bd

        # last_login_at -> last_login
        if "last_login_at" in update_data:
            ll = update_data["last_login_at"]
            if isinstance(ll, str):
                try:
                    ll = datetime.fromisoformat(ll)
                except ValueError:
                    ll = None
            user.last_login = ll

        # обычные поля
        for field in [
            "first_name", "last_name", "middle_name", "email",
            "is_active", "company_id", "department_id", "position_id",
            "role_id", "hire_date", "telegram_username"
        ]:
            if field in update_data:
                setattr(user, field, update_data[field])

        self.db.commit()
        self.db.refresh(user)
        return _to_dict(user)

    def delete_user(self, user_id: int) -> bool:
        user = self.db.query(Users).filter(Users.id == user_id).first()
        if not user:
            return False
        self.db.delete(user)
        self.db.commit()
        return True

    def update_last_login(self, user_id: int) -> Optional[Dict]:
        user = self.db.query(Users).filter(Users.id == user_id).first()
        if not user:
            return None
        user.last_login = datetime.now()
        self.db.commit()
        self.db.refresh(user)
        return _to_dict(user)
