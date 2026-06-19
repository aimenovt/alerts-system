from aio_pika.abc import AbstractChannel
from aio_pika import ExchangeType

from app.messaging import constants


async def declare_topology(channel: AbstractChannel) -> None:
    """Idempotent broker topology: main exchange, queue, and dead-letter queue."""

    events_exchange = await channel.declare_exchange(
        constants.EVENTS_EXCHANGE,
        ExchangeType.TOPIC,
        durable=True,
    )

    dlx_exchange = await channel.declare_exchange(
        constants.EVENTS_DLX_EXCHANGE,
        ExchangeType.TOPIC,
        durable=True,
    )

    processing_queue = await channel.declare_queue(
        constants.EVENTS_PROCESSING_QUEUE,
        durable=True,
        arguments={
            "x-dead-letter-exchange": constants.EVENTS_DLX_EXCHANGE,
            "x-dead-letter-routing-key": constants.EVENTS_PROCESSING_DLQ,
        },
    )
    await processing_queue.bind(events_exchange, routing_key=constants.EVENT_CREATED_ROUTING_KEY)

    dlq = await channel.declare_queue(constants.EVENTS_PROCESSING_DLQ, durable=True)
    await dlq.bind(dlx_exchange, routing_key=constants.EVENTS_PROCESSING_DLQ)
