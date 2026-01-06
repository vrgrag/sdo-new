from __future__ import annotations

from typing import Optional, List, Dict, Any
from datetime import datetime

from sqlalchemy import select, or_, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from models.users import Users
from models.roles import Role


def _to_public_dict(user: Users, role_title: Optional[str] = None) -> Dict[str, Any]:
    return {
        "id": user.id,
        "login": user.login,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "middle_name": user.middle_name,
        "email": user.email,
        "birth_date": user.birth_date.isoformat() if user.birth_date else None,
        "is_active": user.is_active,
        "created_at": user.created_at.isoformat() if user.created_at else None,
        "last_login_at": user.last_login.isoformat() if user.last_login else None,
        "company_id": user.company_id,
        "department_id": user.department_id,
        "position_id": user.position_id,
        "role_id": user.role_id,
        "role": role_title,
        "hire_date": user.hire_date.isoformat() if getattr(user, "hire_date", None) else None,
        "telegram_username": getattr(user, "telegram_username", None),
    }


def _to_private_dict(user: Users) -> Dict[str, Any]:
    d = _to_public_dict(user)
    d["password_hash"] = user.password_hash
    return d


class UserRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all(self) -> List[Dict[str, Any]]:
        stmt = (
            select(Users, Role.title)
            .join(Role, Role.id == Users.role_id, isouter=True)
            .order_by(Users.id.asc())
        )
        res = await self.db.execute(stmt)
        rows = res.all()
        return [_to_public_dict(u, role_title=title) for u, title in rows]

    async def get_by_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        stmt = (
            select(Users, Role.title)
            .join(Role, Role.id == Users.role_id, isouter=True)
            .where(Users.id == user_id)
            .limit(1)
        )
        res = await self.db.execute(stmt)
        row = res.first()
        if not row:
            return None
        user, title = row
        return _to_public_dict(user, role_title=title)

    async def get_by_login(self, login: str) -> Optional[Dict[str, Any]]:
        login = (login or "").strip()
        if not login:
            return None

        stmt = (
            select(Users, Role.title)
            .join(Role, Role.id == Users.role_id, isouter=True)
            .where(func.lower(Users.login) == login.lower())
            .limit(1)
        )
        res = await self.db.execute(stmt)
        row = res.first()
        if not row:
            return None
        user, title = row
        return _to_public_dict(user, role_title=title)

    async def get_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        email = (email or "").strip()
        if not email:
            return None

        stmt = (
            select(Users, Role.title)
            .join(Role, Role.id == Users.role_id, isouter=True)
            .where(func.lower(Users.email) == email.lower())
            .limit(1)
        )
        res = await self.db.execute(stmt)
        row = res.first()
        if not row:
            return None
        user, title = row
        return _to_public_dict(user, role_title=title)

    async def get_by_login_or_email(self, identifier: str) -> Optional[Dict[str, Any]]:
        identifier = (identifier or "").strip()
        if not identifier:
            return None

        stmt = (
            select(Users, Role.title)
            .join(Role, Role.id == Users.role_id, isouter=True)
            .where(
                or_(
                    func.lower(Users.login) == identifier.lower(),
                    func.lower(Users.email) == identifier.lower(),
                )
            )
            .limit(1)
        )
        res = await self.db.execute(stmt)
        row = res.first()
        if not row:
            return None
        user, title = row
        return _to_public_dict(user, role_title=title)

    async def get_auth_user(self, identifier: str) -> Optional[Dict[str, Any]]:
        """
        Приватный метод: возвращает password_hash.
        Используй ТОЛЬКО для /auth/login.
        """
        identifier = (identifier or "").strip()
        if not identifier:
            return None

        stmt = (
            select(Users)
            .where(
                or_(
                    func.lower(Users.login) == identifier.lower(),
                    func.lower(Users.email) == identifier.lower(),
                )
            )
            .limit(1)
        )
        res = await self.db.execute(stmt)
        user = res.scalars().first()
        return _to_private_dict(user) if user else None

    async def create_user(self, user_obj: Users) -> Dict[str, Any]:
        self.db.add(user_obj)
        try:
            await self.db.commit()
        except IntegrityError:
            await self.db.rollback()
            raise
        await self.db.refresh(user_obj)
        return _to_public_dict(user_obj)

    async def update_user(self, user_id: int, update_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        user = await self.db.get(Users, user_id)
        if not user:
            return None

        for field, value in update_data.items():
            setattr(user, field, value)

        try:
            await self.db.commit()
        except IntegrityError:
            await self.db.rollback()
            raise

        await self.db.refresh(user)
        return _to_public_dict(user)

    async def delete_user(self, user_id: int) -> bool:
        user = await self.db.get(Users, user_id)
        if not user:
            return False
        await self.db.delete(user)
        await self.db.commit()
        return True

    async def update_last_login(self, user_id: int) -> Optional[Dict[str, Any]]:
        user = await self.db.get(Users, user_id)
        if not user:
            return None

        user.last_login = datetime.utcnow()

        await self.db.commit()
        await self.db.refresh(user)
        return _to_public_dict(user)
