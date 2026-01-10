# schemas/position.py
from pydantic import BaseModel, Field
from typing import Optional


class PositionBase(BaseModel):
    name: str = Field(..., example="Разработчик", description="Название должности")


class PositionCreate(PositionBase):
    pass


class PositionUpdate(BaseModel):
    name: Optional[str] = Field(None, example="Старший разработчик")


class PositionResponse(PositionBase):
    id: int

    class Config:
        from_attributes = True

