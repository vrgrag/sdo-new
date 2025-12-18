from fastapi import APIRouter, Depends, HTTPException, Request
from typing import List

from core.security import get_current_user
from core.roles import UserRole

from schemas.event import EventCreate, EventResponse
from services.event_service import EventService
from repositories.mock.event_repository import MockEventRepository

router = APIRouter(prefix="/events", tags=["Events"])


def get_event_service() -> EventService:
    return EventService(MockEventRepository())

@router.get("/", response_model=List[EventResponse])
async def list_events(
    service: EventService = Depends(get_event_service),
    current_user: dict = Depends(get_current_user),
):
    role = current_user["role"]
    user_id = current_user["id"]

    events = service.get_all_events()

    # ADMIN / MANAGER → все
    if role in (UserRole.ADMIN.value, UserRole.MANAGER.value):
        return events

    # TEACHER → только те, где он тренер
    if role == UserRole.TRAINER.value:
        return [e for e in events if user_id in e.trainer_ids]

    # STUDENT → только приглашенные
    if role == UserRole.STUDENT.value:
        return [e for e in events if user_id in e.invited_student_ids]

    return []

@router.get("/{event_id}", response_model=EventResponse)
async def get_event(
    event_id: int,
    service: EventService = Depends(get_event_service),
    current_user: dict = Depends(get_current_user),
):
    event = service.get_event(event_id)

    if not event:
        raise HTTPException(status_code=404, detail="Мероприятие не найдено")

    role = current_user["role"]
    user_id = current_user["id"]

    # ADMIN / MANAGER → полный доступ
    if role in (UserRole.ADMIN.value, UserRole.MANAGER.value):
        return event

    # TEACHER → только если он тренер
    if role == UserRole.TRAINER.value:
        if user_id in event.trainer_ids:
            return event
        raise HTTPException(status_code=403, detail="Нет доступа")

    # STUDENT → только если приглашен
    if role == UserRole.STUDENT.value:
        if user_id in event.invited_student_ids:
            return event
        raise HTTPException(status_code=403, detail="Нет доступа")

    raise HTTPException(status_code=403, detail="Недостаточно прав")

@router.post("/", response_model=EventResponse, status_code=201)
async def create_event(
    request: Request,
    event_data: EventCreate,
    service: EventService = Depends(get_event_service),
    current_user: dict = Depends(get_current_user),
):
    print(await request.body())

    if current_user["role"] not in (UserRole.ADMIN.value, UserRole.MANAGER.value):
        raise HTTPException(status_code=403, detail="Недостаточно прав")

    return service.create_event(event_data)

@router.put("/{event_id}", response_model=EventResponse)
async def update_event(
    event_id: int,
    event_data: EventCreate,
    service: EventService = Depends(get_event_service),
    current_user: dict = Depends(get_current_user),
):
    if current_user["role"] not in (UserRole.ADMIN.value, UserRole.MANAGER.value):
        raise HTTPException(status_code=403, detail="Недостаточно прав")

    return service.update_event(event_id, event_data)

@router.delete("/{event_id}", status_code=204)
async def delete_event(
    event_id: int,
    service: EventService = Depends(get_event_service),
    current_user: dict = Depends(get_current_user),
):
    if current_user["role"] not in (UserRole.ADMIN.value, UserRole.MANAGER.value):
        raise HTTPException(status_code=403, detail="Недостаточно прав")

    service.delete_event(event_id)
    return None

@router.post("/{event_id}/register/{student_id}", status_code=204)
async def register_student_to_event(
    event_id: int,
    student_id: int,
    service: EventService = Depends(get_event_service),
    current_user: dict = Depends(get_current_user),
):
    event = service.get_event(event_id)
    role = current_user["role"]
    user_id = current_user["id"]

    if role in (UserRole.ADMIN.value, UserRole.MANAGER.value):
        event.invited_student_ids.append(student_id)
        return None

    if role == UserRole.TRAINER.value:
        if user_id not in event.trainer_ids:
            raise HTTPException(status_code=403, detail="Вы не тренер события")
        event.invited_student_ids.append(student_id)
        return None

    if role == UserRole.STUDENT.value:
        if student_id != user_id:
            raise HTTPException(status_code=403, detail="Можно записывать только себя")

        if student_id not in event.invited_student_ids:
            raise HTTPException(status_code=403, detail="Событие доступно только по приглашению")

        return None

    raise HTTPException(status_code=403, detail="Недостаточно прав")

@router.delete("/{event_id}/register/{student_id}", status_code=204)
async def unregister_student_from_event(
    event_id: int,
    student_id: int,
    service: EventService = Depends(get_event_service),
    current_user: dict = Depends(get_current_user),
):
    event = service.get_event(event_id)
    role = current_user["role"]
    user_id = current_user["id"]
    if role in (UserRole.ADMIN.value, UserRole.MANAGER.value):
        if student_id in event.invited_student_ids:
            event.invited_student_ids.remove(student_id)
        return None

    if role == UserRole.TRAINER.value:
        if user_id not in event.trainer_ids:
            raise HTTPException(status_code=403, detail="Вы не тренер этого события")
        if student_id in event.invited_student_ids:
            event.invited_student_ids.remove(student_id)
        return None
    if role == UserRole.STUDENT.value:
        if student_id != user_id:
            raise HTTPException(status_code=403, detail="Можно отписать только себя")

        if student_id not in event.invited_student_ids:
            raise HTTPException(status_code=403, detail="Вы не приглашены")

        event.invited_student_ids.remove(student_id)
        return None

    raise HTTPException(status_code=403, detail="Недостаточно прав")
