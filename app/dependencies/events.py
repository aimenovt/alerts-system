from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db_session
from app.dependencies.messaging import get_event_publisher
from app.messaging.publisher import EventPublisher
from app.services.event_service import EventService


async def get_event_service(
    session: AsyncSession = Depends(get_db_session),
    publisher: EventPublisher | None = Depends(get_event_publisher),
) -> EventService:
    return EventService(session=session, publisher=publisher)
