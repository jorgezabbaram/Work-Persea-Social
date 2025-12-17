import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlalchemy.ext.asyncio import AsyncSession

from api.routes import router
from application.inventory_service import InventoryService
from infrastructure.database import get_db_session
from infrastructure.repository import InventoryRepository
from infrastructure.message_queue import message_queue

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def setup_event_listeners():
    """Setup event listeners for order events"""
    async def handle_order_events(event):
        async for session in get_db_session():
            repository = InventoryRepository(session)
            service = InventoryService(repository, message_queue)
            
            if event.event_type == "OrderCreated":
                await service.handle_order_created(event)
            break

    # Subscribe to order events
    await message_queue.subscribe_to_events(
        ["order.created"],
        handle_order_events
    )


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting Inventory Service...")
    await message_queue.connect()
    
    # Setup event listeners in background
    asyncio.create_task(setup_event_listeners())
    
    yield
    
    # Shutdown
    logger.info("Shutting down Inventory Service...")
    await message_queue.close()


app = FastAPI(
    title="Inventory Service",
    description="Microservice for inventory management",
    version="1.0.0",
    lifespan=lifespan
)

app.include_router(router)


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "inventory-service"}