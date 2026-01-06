from typing import Optional
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from models.roles import Role


class RoleRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_title_by_id(self, role_id: int) -> Optional[str]:
        res = await self.db.execute(
            select(Role.title).where(Role.id == role_id).limit(1)
        )
        return res.scalar_one_or_none()

    async def get_id_by_title(self, title: str) -> Optional[int]:
        title = (title or "").strip()
        if not title:
            return None
        res = await self.db.execute(
            select(Role.id).where(func.lower(Role.title) == title.lower()).limit(1)
        )
        return res.scalar_one_or_none()
