import logging

from sqlalchemy.ext.asyncio import AsyncSession

from app.messaging.publisher import EventPublisher
from app.models.event import Event
from app.repositories.event_repository import EventRepository
from app.schemas.event import EventCreate

logger = logging.getLogger(__name__)


class EventService:
    def __init__(self, session: AsyncSession, publisher: EventPublisher | None = None):
        self.events = EventRepository(session)
        self.publisher = publisher

    async def create_event(self, payload: EventCreate, owner_id: str) -> Event:
        event = await self.events.create(
            event_type=payload.event_type,
            payload=payload.payload,
            owner_id=owner_id,
        )

        if self.publisher is not None:
            try:
                await self.publisher.publish_event_created(event)
            except Exception:
                logger.exception(
                    "Failed to publish event_id=%s to RabbitMQ; event remains queued in DB",
                    event.id,
                )

        return event

    async def list_events(self, owner_id: str) -> list[Event]:
        return await self.events.list_by_owner(owner_id=owner_id)
