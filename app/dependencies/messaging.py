from app.core.config import settings
from app.messaging.connection import rabbitmq_manager
from app.messaging.publisher import EventPublisher


async def get_event_publisher() -> EventPublisher | None:
    if not settings.RABBITMQ_ENABLED:
        return None

    channel = await rabbitmq_manager.get_channel()
    return EventPublisher(channel)
