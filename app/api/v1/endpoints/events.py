from fastapi import APIRouter, Depends, status

from app.dependencies.auth import get_current_user
from app.dependencies.events import get_event_service
from app.models.user import User
from app.schemas.event import EventCreate, EventRead
from app.services.event_service import EventService

router = APIRouter()


@router.post("", response_model=EventRead, status_code=status.HTTP_201_CREATED)
async def create_event(
    payload: EventCreate,
    current_user: User = Depends(get_current_user),
    service: EventService = Depends(get_event_service),
) -> EventRead:
    event = await service.create_event(payload=payload, owner_id=current_user.id)
    return EventRead.model_validate(event)


@router.get("", response_model=list[EventRead])
async def list_events(
    current_user: User = Depends(get_current_user),
    service: EventService = Depends(get_event_service),
) -> list[EventRead]:
    events = await service.list_events(owner_id=current_user.id)
    return [EventRead.model_validate(event) for event in events]
