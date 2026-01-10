from typing import Optional, List, Dict, Any
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from models.positions import Position


def _to_dict(position: Position) -> Dict[str, Any]:
    return {
        "id": position.id,
        "name": position.name,
    }


class PositionRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all(self) -> List[Dict[str, Any]]:
        stmt = select(Position).order_by(Position.id.asc())
        res = await self.db.execute(stmt)
        positions = res.scalars().all()
        return [_to_dict(p) for p in positions]

    async def get_by_id(self, position_id: int) -> Optional[Dict[str, Any]]:
        position = await self.db.get(Position, position_id)
        if not position:
            return None
        return _to_dict(position)

    async def get_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        stmt = select(Position).where(Position.name == name).limit(1)
        res = await self.db.execute(stmt)
        position = res.scalar_one_or_none()
        return _to_dict(position) if position else None

    async def create(self, position_data: Dict[str, Any]) -> Dict[str, Any]:
        position = Position(name=position_data["name"])
        self.db.add(position)
        try:
            await self.db.commit()
        except IntegrityError:
            await self.db.rollback()
            raise
        await self.db.refresh(position)
        return _to_dict(position)

    async def update(self, position_id: int, update_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        position = await self.db.get(Position, position_id)
        if not position:
            return None

        for field, value in update_data.items():
            if value is not None:
                setattr(position, field, value)

        try:
            await self.db.commit()
        except IntegrityError:
            await self.db.rollback()
            raise

        await self.db.refresh(position)
        return _to_dict(position)

    async def delete(self, position_id: int) -> bool:
        position = await self.db.get(Position, position_id)
        if not position:
            return False
        await self.db.delete(position)
        await self.db.commit()
        return True

