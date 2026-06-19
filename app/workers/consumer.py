import logging

from aio_pika.abc import AbstractIncomingMessage

from app.db.session import AsyncSessionLocal
from app.messaging import constants
from app.messaging.connection import RabbitMQManager
from app.messaging.schemas import EventMessage
from app.services.event_processor import EventProcessor

logger = logging.getLogger(__name__)


class EventConsumer:
    """Consumes event.created messages and runs EventProcessor."""

    def __init__(self, manager: RabbitMQManager) -> None:
        self._manager = manager

    async def run(self) -> None:
        channel = await self._manager.get_channel()
        queue = await channel.get_queue(constants.EVENTS_PROCESSING_QUEUE)

        logger.info("Worker listening on queue=%s", constants.EVENTS_PROCESSING_QUEUE)
        async with queue.iterator() as queue_iter:
            async for message in queue_iter:
                await self._handle_message(message)

    async def _handle_message(self, message: AbstractIncomingMessage) -> None:
        async with message.process(requeue=False, ignore_processed=True):
            try:
                payload = EventMessage.model_validate_json(message.body)
            except Exception:
                logger.exception("Invalid broker message; sending to DLQ")
                raise

            try:
                async with AsyncSessionLocal() as session:
                    processor = EventProcessor(session)
                    await processor.process(payload.event_id)
            except ValueError:
                logger.exception("Permanent processing error for event_id=%s", payload.event_id)
                raise
            except Exception:
                logger.exception("Failed to process event_id=%s", payload.event_id)
                async with AsyncSessionLocal() as session:
                    processor = EventProcessor(session)
                    await processor.mark_failed(payload.event_id)
                raise
