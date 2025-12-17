from fastapi import FastAPI
from contextlib import asynccontextmanager
import logging

from api.routes import router
from infrastructure.message_queue import MessageQueue

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

message_queue = MessageQueue()

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting Notification Service...")
    await message_queue.connect()
    await message_queue.setup_consumers()
    yield
    await message_queue.disconnect()

app = FastAPI(
    title="Notification Service",
    description="Handles notifications in the order processing system",
    version="1.0.0",
    lifespan=lifespan
)

app.include_router(router)