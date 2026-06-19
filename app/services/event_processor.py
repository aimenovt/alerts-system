import logging

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.event import Event, EventStatus
from app.repositories.event_repository import EventRepository

logger = logging.getLogger(__name__)


class EventProcessor:
    """Handles domain processing for consumed broker messages."""

    def __init__(self, session: AsyncSession):
        self.events = EventRepository(session)

    async def process(self, event_id: str) -> None:
        event = await self.events.get_by_id(event_id)
        if event is None:
            raise ValueError(f"Event {event_id} not found")

        if event.status == EventStatus.processed:
            logger.info("Skipping event_id=%s with status=%s", event_id, event.status)
            return

        await self.events.update_status(event_id, EventStatus.processing)
        await self._handle(event)
        await self.events.update_status(event_id, EventStatus.processed)
        logger.info("Processed event_id=%s type=%s", event.id, event.event_type)

    async def _handle(self, event: Event) -> None:
        # Extension point: route by event.event_type to dedicated handlers.
        logger.info("Handling event_id=%s payload=%s", event.id, event.payload)

    async def mark_failed(self, event_id: str) -> None:
        await self.events.update_status(event_id, EventStatus.failed)
