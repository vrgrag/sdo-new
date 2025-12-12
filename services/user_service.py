# services/user_service.py
from typing import List, Dict, Any

from fastapi import HTTPException, status

from repositories.mock.user_repository import user_repository
from core.roles import UserRole


class UserService:


    def _get_role(self, user: Dict[str, Any]) -> UserRole | None:
        role_value = user.get("role")
        try:
            return UserRole(role_value)
        except ValueError:
            return None

    def apply_visibility(
        self,
        all_users: List[Dict[str, Any]],
        current_user: Dict[str, Any],
    ) -> List[Dict[str, Any]]:

        role = self._get_role(current_user)
        if not role:
            return []
        if role in (UserRole.ADMIN, UserRole.MANAGER):
            return all_users

        if role == UserRole.STUDENT:
            return [u for u in all_users if u.get("id") == current_user.get("id")]


        if role == UserRole.TRAINER:
            trainer_id = current_user["id"]
            from repositories.mock.course_repository import course_repository
            trainer_courses = course_repository.get_courses_by_trainer(trainer_id)

            students_ids = set()
            for course in trainer_courses:
                enrolled = course_repository.get_students_by_course(course["id"])
                for st in enrolled:
                    students_ids.add(st["id"])
            return [u for u in all_users if u.get("id") in students_ids]

        return []

    def get_visible_users(self, current_user: Dict[str, Any]) -> List[Dict[str, Any]]:
        all_users = user_repository.get_all()
        return self.apply_visibility(all_users, current_user)

    def create_user(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        if user_repository.get_by_login(user_data["login"]):
            raise HTTPException(status_code=400, detail="Логин уже занят")

        if user_repository.get_by_email(user_data["email"]):
            raise HTTPException(status_code=400, detail="Email уже занят")

        data = user_data.copy()
        data.pop("password_confirm", None)

        created = user_repository.create_user(data)
        return created

    def get_by_id(self, user_id: int, current_user: Dict[str, Any]) -> Dict[str, Any]:
        user = user_repository.get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="Пользователь не найден")

        visible = self.apply_visibility([user], current_user)
        if not visible:
            raise HTTPException(status_code=403, detail="Недостаточно прав для просмотра")

        return user

    def update_user(
        self,
        user_id: int,
        update_data: Dict[str, Any],
        current_user: Dict[str, Any],
    ) -> Dict[str, Any]:
        existing = user_repository.get_by_id(user_id)
        if not existing:
            raise HTTPException(status_code=404, detail="Пользователь не найден")

        if not self.apply_visibility([existing], current_user):
            raise HTTPException(status_code=403, detail="Недостаточно прав для изменения")

        new_login = update_data.get("login")
        if new_login and new_login != existing["login"]:
            other = user_repository.get_by_login(new_login)
            if other and other["id"] != user_id:
                raise HTTPException(status_code=400, detail="Логин уже занят")

        new_email = update_data.get("email")
        if new_email and new_email != existing["email"]:
            other = user_repository.get_by_email(new_email)
            if other and other["id"] != user_id:
                raise HTTPException(status_code=400, detail="Email уже занят")

        data = update_data.copy()
        data.pop("password_confirm", None)

        updated = user_repository.update_user(user_id, data)
        if not updated:
            raise HTTPException(status_code=404, detail="Пользователь не найден при обновлении")

        return updated

    def delete_user(self, user_id: int, current_user: Dict[str, Any]) -> Dict[str, Any]:
        existing = user_repository.get_by_id(user_id)
        if not existing:
            raise HTTPException(status_code=404, detail="Пользователь не найден")

        if not self.apply_visibility([existing], current_user):
            raise HTTPException(status_code=403, detail="Недостаточно прав для удаления")

        if not user_repository.delete_user(user_id):
            raise HTTPException(status_code=404, detail="Пользователь не найден при удалении")

        return {"detail": "Пользователь удалён"}


user_service = UserService()
