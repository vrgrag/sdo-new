from __future__ import annotations

from typing import List, Dict, Any
from datetime import datetime

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from core.security import hash_password
from repositories.mock.user_repository import UserRepository
from repositories.mock.role_repository import RoleRepository


def _norm_role_title(title: str | None) -> str:
    return (title or "").strip().lower()


class UserService:
    async def _get_current_role_title(self, db: AsyncSession, current_user: Dict[str, Any]) -> str:
        role_id = current_user.get("role_id")
        if not role_id:
            return ""
        return _norm_role_title(await RoleRepository(db).get_title_by_id(int(role_id)))

    async def _ensure_admin_or_manager(self, db: AsyncSession, current_user: Dict[str, Any]) -> None:
        role_title = await self._get_current_role_title(db, current_user)
        if role_title not in ("admin", "manager"):
            raise HTTPException(status_code=403, detail="Недостаточно прав")

    async def apply_visibility(
        self,
        db: AsyncSession,
        all_users: List[Dict[str, Any]],
        current_user: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        role_title = await self._get_current_role_title(db, current_user)

        # admin/manager видят всех
        if role_title in ("admin", "manager"):
            return all_users

        # student видит только себя
        if role_title == "student":
            return [u for u in all_users if u.get("id") == current_user.get("id")]

        # trainer видит только студентов своих курсов (если у тебя это реально так)
        if role_title == "trainer":
            trainer_id = current_user.get("id")
            if not trainer_id:
                return []

            from repositories.mock.course_repository import course_repository  # как у тебя сейчас
            trainer_courses = course_repository.get_courses_by_trainer(trainer_id)

            students_ids = set()
            for course in trainer_courses:
                enrolled = course_repository.get_students_by_course(course["id"])
                for st in enrolled:
                    students_ids.add(st["id"])

            return [u for u in all_users if u.get("id") in students_ids]

        return []

    async def get_visible_users(self, db: AsyncSession, current_user: Dict[str, Any]) -> List[Dict[str, Any]]:
        repo = UserRepository(db)
        all_users = await repo.get_all()
        return await self.apply_visibility(db, all_users, current_user)

    async def create_user(
        self,
        db: AsyncSession,
        user_data: Dict[str, Any],
        current_user: Dict[str, Any],
    ) -> Dict[str, Any]:
        await self._ensure_admin_or_manager(db, current_user)

        repo = UserRepository(db)

        if await repo.get_by_login(user_data["login"]):
            raise HTTPException(status_code=400, detail="Логин уже занят")
        if await repo.get_by_email(user_data["email"]):
            raise HTTPException(status_code=400, detail="Email уже занят")

        role_title = (user_data.get("role") or "").strip()
        if not role_title:
            raise HTTPException(status_code=400, detail="role обязателен")

        role_repo = RoleRepository(db)
        role_id = await role_repo.get_id_by_title(role_title)
        if role_id is None:
            raise HTTPException(status_code=400, detail=f"Неизвестная роль: {role_title}")

        user_data["role_id"] = role_id
        user_data.pop("role", None)

        raw_password = user_data.pop("password")
        user_data.pop("password_confirm", None)

        from models.users import Users

        # ВАЖНО: у тебя TIMESTAMP WITHOUT TIME ZONE => используем naive datetime
        now = datetime.utcnow()

        user = Users(
            login=user_data.get("login"),
            first_name=user_data.get("first_name") or "",
            last_name=user_data.get("last_name") or "",
            middle_name=user_data.get("middle_name"),
            email=str(user_data.get("email")).strip().lower(),
            password_hash=hash_password(raw_password),
            created_at=user_data.get("created_at") or now,
            is_active=user_data.get("is_active", True),
            birth_date=user_data.get("birth_date"),
            company_id=user_data.get("company_id"),
            department_id=user_data.get("department_id"),
            position_id=user_data.get("position_id"),
            role_id=user_data.get("role_id"),
            hire_date=user_data.get("hire_date"),
            telegram_username=user_data.get("telegram_username"),
        )

        try:
            return await repo.create_user(user)
        except Exception:
            raise HTTPException(status_code=400, detail="Ошибка создания пользователя")

    async def get_by_id(self, db: AsyncSession, user_id: int, current_user: Dict[str, Any]) -> Dict[str, Any]:
        repo = UserRepository(db)
        user = await repo.get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="Пользователь не найден")

        visible = await self.apply_visibility(db, [user], current_user)
        if not visible:
            raise HTTPException(status_code=403, detail="Недостаточно прав для просмотра")

        return user

    async def update_user(
        self,
        db: AsyncSession,
        user_id: int,
        update_data: Dict[str, Any],
        current_user: Dict[str, Any],
    ) -> Dict[str, Any]:
        repo = UserRepository(db)
        existing = await repo.get_by_id(user_id)
        if not existing:
            raise HTTPException(status_code=404, detail="Пользователь не найден")

        visible = await self.apply_visibility(db, [existing], current_user)
        if not visible:
            raise HTTPException(status_code=403, detail="Недостаточно прав для изменения")

        new_login = update_data.get("login")
        if new_login and new_login != existing["login"]:
            other = await repo.get_by_login(new_login)
            if other and other["id"] != user_id:
                raise HTTPException(status_code=400, detail="Логин уже занят")

        new_email = update_data.get("email")
        if new_email and new_email != existing["email"]:
            other = await repo.get_by_email(new_email)
            if other and other["id"] != user_id:
                raise HTTPException(status_code=400, detail="Email уже занят")

        if update_data.get("password"):
            raw_password = update_data.pop("password")
            update_data.pop("password_confirm", None)
            update_data["password_hash"] = hash_password(raw_password)

        update_data.pop("password_confirm", None)

        if "role" in update_data:
            role_title = (update_data.get("role") or "").strip()
            if not role_title:
                raise HTTPException(status_code=400, detail="role не может быть пустым")

            role_repo = RoleRepository(db)
            role_id = await role_repo.get_id_by_title(role_title)
            if role_id is None:
                raise HTTPException(status_code=400, detail=f"Неизвестная роль: {role_title}")

            update_data["role_id"] = role_id
            update_data.pop("role", None)

        # защита: если фронт всё же пришлёт role_id — лучше запретить
        update_data.pop("role_id", None)

        try:
            updated = await repo.update_user(user_id, update_data)
        except Exception:
            raise HTTPException(status_code=400, detail="Ошибка обновления пользователя")

        if not updated:
            raise HTTPException(status_code=404, detail="Пользователь не найден при обновлении")

        return updated

    async def delete_user(self, db: AsyncSession, user_id: int, current_user: Dict[str, Any]) -> Dict[str, Any]:
        repo = UserRepository(db)
        existing = await repo.get_by_id(user_id)
        if not existing:
            raise HTTPException(status_code=404, detail="Пользователь не найден")

        visible = await self.apply_visibility(db, [existing], current_user)
        if not visible:
            raise HTTPException(status_code=403, detail="Недостаточно прав для удаления")

        ok = await repo.delete_user(user_id)
        if not ok:
            raise HTTPException(status_code=404, detail="Пользователь не найден при удалении")

        return {"detail": "Пользователь удалён"}


user_service = UserService()
