import asyncio
import logging

from app.core.config import settings
from app.messaging.connection import rabbitmq_manager
from app.workers.consumer import EventConsumer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def main() -> None:
    if not settings.RABBITMQ_ENABLED:
        logger.error("RABBITMQ_ENABLED=false; worker cannot start")
        return

    await rabbitmq_manager.connect()
    consumer = EventConsumer(rabbitmq_manager)

    try:
        await consumer.run()
    finally:
        await rabbitmq_manager.close()


if __name__ == "__main__":
    asyncio.run(main())
