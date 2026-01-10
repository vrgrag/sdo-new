# api/v1/events.py
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.db import get_db
from core.security import get_current_user
from core.roles import UserRole

from schemas.event import EventCreate, EventUpdate, EventOut
from services.event_service import EventService

router = APIRouter(prefix="/events", tags=["Events"])


def get_event_service(db: AsyncSession = Depends(get_db)) -> EventService:
    return EventService(db)


@router.get("/", response_model=List[EventOut])
async def list_events(
    service: EventService = Depends(get_event_service),
    current_user: dict = Depends(get_current_user),
):
    role = current_user["role"]
    user_id = current_user["id"]

    events = await service.list_events_with_participants()

    if role in (UserRole.ADMIN.value, UserRole.MANAGER.value):
        return events

    if role == UserRole.TRAINER.value:
        return [e for e in events if e.trainer_id == user_id]

    if role == UserRole.STUDENT.value:
        # приглашения лучше делать через attendance (мы можем добавить join-фильтр)
        return []

    return []


@router.get("/{event_id}", response_model=EventOut)
async def get_event(
    event_id: int,
    service: EventService = Depends(get_event_service),
    current_user: dict = Depends(get_current_user),
):
    role = current_user["role"]
    user_id = current_user["id"]

    event = await service.get_event_with_participants(event_id)

    if role in (UserRole.ADMIN.value, UserRole.MANAGER.value):
        return event

    if role == UserRole.TRAINER.value:
        if event.trainer_id == user_id:
            return event
        raise HTTPException(status_code=403, detail="Нет доступа")

    if role == UserRole.STUDENT.value:
        return event  # или запретить, если доступ только по приглашению

    raise HTTPException(status_code=403, detail="Недостаточно прав")


@router.post("/", response_model=EventOut, status_code=status.HTTP_201_CREATED)
async def create_event(
    data: EventCreate,
    service: EventService = Depends(get_event_service),
    current_user: dict = Depends(get_current_user),
):
    if current_user["role"] not in (UserRole.ADMIN.value, UserRole.MANAGER.value):
        raise HTTPException(status_code=403, detail="Недостаточно прав")

    return await service.create_event(data, current_user=current_user)


@router.patch("/{event_id}", response_model=EventOut)
async def update_event(
    event_id: int,
    data: EventUpdate,
    service: EventService = Depends(get_event_service),
    current_user: dict = Depends(get_current_user),
):
    if current_user["role"] not in (UserRole.ADMIN.value, UserRole.MANAGER.value):
        raise HTTPException(status_code=403, detail="Недостаточно прав")

    return await service.update_event(event_id, data)


@router.delete("/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_event(
    event_id: int,
    service: EventService = Depends(get_event_service),
    current_user: dict = Depends(get_current_user),
):
    if current_user["role"] not in (UserRole.ADMIN.value, UserRole.MANAGER.value):
        raise HTTPException(status_code=403, detail="Недостаточно прав")

    await service.delete_event(event_id)
    return None


@router.get("/{event_id}/participants", response_model=List[dict])
async def get_event_participants(
    event_id: int,
    service: EventService = Depends(get_event_service),
    current_user: dict = Depends(get_current_user),
):
    """Получить список участников мероприятия"""
    role = current_user["role"]
    user_id = current_user["id"]
    
    # Проверяем доступ
    event = await service.get_event(event_id)
    
    if role not in (UserRole.ADMIN.value, UserRole.MANAGER.value):
        if role == UserRole.TRAINER.value:
            if event.trainer_id != user_id:
                raise HTTPException(status_code=403, detail="Нет доступа")
        else:
            raise HTTPException(status_code=403, detail="Недостаточно прав")
    
    participants = await service.get_participants(event_id)
    return participants


@router.delete("/{event_id}/participants/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_participant(
    event_id: int,
    user_id: int,
    service: EventService = Depends(get_event_service),
    current_user: dict = Depends(get_current_user),
):
    """Удалить участника из мероприятия"""
    role = current_user["role"]
    current_user_id = current_user["id"]
    
    # Проверяем доступ
    event = await service.get_event(event_id)
    
    if role not in (UserRole.ADMIN.value, UserRole.MANAGER.value):
        if role == UserRole.TRAINER.value:
            if event.trainer_id != current_user_id:
                raise HTTPException(status_code=403, detail="Нет доступа")
        else:
            raise HTTPException(status_code=403, detail="Недостаточно прав")
    
    # Проверяем превышение лимита мест (если нужно)
    event_with_participants = await service.get_event_with_participants(event_id)
    
    # Удаляем участника
    await service.remove_participant(event_id, user_id)
    
    return None
