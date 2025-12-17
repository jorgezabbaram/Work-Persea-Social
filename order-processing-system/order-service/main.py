import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlalchemy.ext.asyncio import AsyncSession

from api.routes import router
from application.order_service import OrderService
from infrastructure.database import get_db_session
from infrastructure.repository import OrderRepository
from infrastructure.message_queue import message_queue

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def setup_event_listeners():
    """Setup event listeners for payment events"""
    async def handle_payment_events(event):
        async for session in get_db_session():
            repository = OrderRepository(session)
            service = OrderService(repository, message_queue)
            
            if event.event_type == "PaymentProcessed":
                await service.handle_payment_processed(event)
            elif event.event_type == "PaymentFailed":
                await service.handle_payment_failed(event)
            break

    # Subscribe to payment events
    await message_queue.subscribe_to_events(
        ["payment.processed", "payment.failed"],
        handle_payment_events
    )


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting Order Service...")
    await message_queue.connect()
    
    # Setup event listeners in background
    asyncio.create_task(setup_event_listeners())
    
    yield
    
    # Shutdown
    logger.info("Shutting down Order Service...")
    await message_queue.close()


app = FastAPI(
    title="Order Service",
    description="Microservice for order processing",
    version="1.0.0",
    lifespan=lifespan
)

app.include_router(router)


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "order-service"}