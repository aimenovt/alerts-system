import asyncio
import logging

import aio_pika
from aio_pika.abc import AbstractChannel, AbstractRobustConnection

from app.core.config import settings
from app.messaging.topology import declare_topology

logger = logging.getLogger(__name__)


class RabbitMQManager:
    """Shared robust connection for API publisher and worker consumer."""

    def __init__(self) -> None:
        self._connection: AbstractRobustConnection | None = None
        self._channel: AbstractChannel | None = None
        self._connect_lock = asyncio.Lock()

    @property
    def is_connected(self) -> bool:
        return self._connection is not None and not self._connection.is_closed

    async def connect(self) -> None:
        if not settings.RABBITMQ_ENABLED:
            logger.info("RabbitMQ disabled; skipping connection")
            return

        if self.is_connected:
            return

        async with self._connect_lock:
            if self.is_connected:
                return

            self._connection = await aio_pika.connect_robust(settings.rabbitmq_url)
            self._channel = await self._connection.channel()
            await self._channel.set_qos(prefetch_count=settings.RABBITMQ_PREFETCH_COUNT)
            await declare_topology(self._channel)
            logger.info("RabbitMQ connected")

    async def close(self) -> None:
        if self._channel is not None and not self._channel.is_closed:
            await self._channel.close()
        if self._connection is not None and not self._connection.is_closed:
            await self._connection.close()
        self._channel = None
        self._connection = None
        logger.info("RabbitMQ connection closed")

    async def get_channel(self) -> AbstractChannel:
        if not settings.RABBITMQ_ENABLED:
            raise RuntimeError("RabbitMQ is disabled")

        if not self.is_connected or self._channel is None or self._channel.is_closed:
            await self.connect()

        assert self._channel is not None
        return self._channel


rabbitmq_manager = RabbitMQManager()
