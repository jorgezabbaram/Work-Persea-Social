import asyncio
import json
import logging
import os
from typing import Callable

import aio_pika
from aio_pika import connect_robust
from aio_pika.abc import AbstractIncomingMessage

from domain.events import OrderConfirmed, PaymentProcessed, PaymentFailed, OrderCompleted

logger = logging.getLogger(__name__)


class MessageQueue:
    def __init__(self):
        self.connection = None
        self.channel = None
        self.exchange = None
        self.rabbitmq_url = os.getenv("RABBITMQ_URL", "amqp://admin:admin@localhost:5672/")

    async def connect(self) -> None:
        self.connection = await connect_robust(self.rabbitmq_url)
        self.channel = await self.connection.channel()
        self.exchange = await self.channel.declare_exchange(
            "order_events", aio_pika.ExchangeType.TOPIC, durable=True
        )

    async def subscribe_to_events(self, routing_keys: list[str], callback: Callable) -> None:
        if not self.channel:
            await self.connect()

        queue = await self.channel.declare_queue("", exclusive=True)

        for routing_key in routing_keys:
            await queue.bind(self.exchange, routing_key)

        async def message_handler(message: AbstractIncomingMessage) -> None:
            async with message.process():
                try:
                    event_data = json.loads(message.body.decode())
                    event_type = message.headers.get("event_type")
                    
                    # Parse specific event types
                    event = None
                    if event_type == "OrderConfirmed":
                        event = OrderConfirmed(**event_data)
                    elif event_type == "PaymentProcessed":
                        event = PaymentProcessed(**event_data)
                    elif event_type == "PaymentFailed":
                        event = PaymentFailed(**event_data)
                    elif event_type == "OrderCompleted":
                        event = OrderCompleted(**event_data)
                    
                    if event:
                        await callback(event)
                        logger.info(f"Processed event {event_type}")
                except Exception as e:
                    logger.error(f"Error processing message: {e}")
                    raise

        await queue.consume(message_handler)

    async def close(self) -> None:
        if self.connection:
            await self.connection.close()
    async def setup_consumers(self) -> None:
        # Compatibility shim: if service expects a setup_consumers method,
        # provide a no-op implementation here. Consumers can be registered
        # via `subscribe_to_events` when needed.
        return None

    async def disconnect(self) -> None:
        # Compatibility shim for `disconnect` used in some lifespans
        await self.close()


# Global instance
message_queue = MessageQueue()