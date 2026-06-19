import logging
from datetime import datetime, timezone

import aio_pika
from aio_pika.abc import AbstractChannel

from app.core.config import settings
from app.messaging import constants
from app.messaging.schemas import EventMessage
from app.models.event import Event

logger = logging.getLogger(__name__)


class EventPublisher:
    """Publishes persisted events to RabbitMQ for async processing."""

    def __init__(self, channel: AbstractChannel) -> None:
        self._channel = channel

    async def publish_event_created(self, event: Event) -> None:
        if not settings.RABBITMQ_ENABLED:
            return

        message = EventMessage.from_event(event)
        exchange = await self._channel.get_exchange(constants.EVENTS_EXCHANGE)
        await exchange.publish(
            aio_pika.Message(
                body=message.model_dump_json().encode(),
                content_type="application/json",
                delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
                message_id=event.id,
                type=constants.EVENT_CREATED_ROUTING_KEY,
                app_id="alerts-api",
                timestamp=datetime.now(timezone.utc),
            ),
            routing_key=constants.EVENT_CREATED_ROUTING_KEY,
            mandatory=True,
        )
        logger.info("Published event.created for event_id=%s", event.id)
