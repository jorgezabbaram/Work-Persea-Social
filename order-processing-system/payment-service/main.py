import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlalchemy.ext.asyncio import AsyncSession

from api.routes import router
from application.payment_service import PaymentService
from infrastructure.database import get_db_session
from infrastructure.repository import PaymentRepository
from infrastructure.message_queue import message_queue

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def setup_event_listeners():
    """Setup event listeners for inventory events"""
    async def handle_inventory_events(event):
        async for session in get_db_session():
            repository = PaymentRepository(session)
            service = PaymentService(repository, message_queue)
            
            if event.event_type == "InventoryReserved":
                await service.handle_inventory_reserved(event)
            break

    # Subscribe to inventory events
    await message_queue.subscribe_to_events(
        ["inventory.reserved"],
        handle_inventory_events
    )


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting Payment Service...")
    await message_queue.connect()
    
    # Setup event listeners in background
    asyncio.create_task(setup_event_listeners())
    
    yield
    
    # Shutdown
    logger.info("Shutting down Payment Service...")
    await message_queue.close()


app = FastAPI(
    title="Payment Service",
    description="Microservice for payment processing with retry logic",
    version="1.0.0",
    lifespan=lifespan
)

app.include_router(router)


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "payment-service"}