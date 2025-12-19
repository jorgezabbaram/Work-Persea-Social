from fastapi import FastAPI
from contextlib import asynccontextmanager
import logging

from api.routes import router
from infrastructure.message_queue import MessageQueue
from application.notification_service import NotificationService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

message_queue = MessageQueue()
notification_service = NotificationService()

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting Notification Service...")
    await message_queue.connect()
    
    async def event_handler(event):
        logger.info(f"Received event: {event}")
        if hasattr(event, "order_id"):
             if event.__class__.__name__ == "OrderConfirmed":
                 await notification_service.handle_order_confirmed(event)
             elif event.__class__.__name__ == "PaymentProcessed":
                 await notification_service.handle_payment_processed(event)
             elif event.__class__.__name__ == "PaymentFailed":
                 await notification_service.handle_payment_failed(event)
             elif event.__class__.__name__ == "OrderCompleted":
                 await notification_service.handle_order_completed(event)

    await message_queue.subscribe_to_events(
        ["order.confirmed", "payment.processed", "payment.failed", "order.completed"],
        event_handler
    )
    
    yield
    await message_queue.disconnect()

app = FastAPI(
    title="Notification Service",
    lifespan=lifespan
)

app.state.notification_service = notification_service

app.include_router(router)