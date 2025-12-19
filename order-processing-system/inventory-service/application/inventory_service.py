import logging
from typing import Optional
from uuid import UUID

from domain.events import OrderCreated, InventoryReserved, InventoryUnavailable
from domain.models import InventoryItem
from infrastructure.repository import InventoryRepository
from infrastructure.message_queue import MessageQueue

logger = logging.getLogger(__name__)


class InventoryService:
    def __init__(self, repository: InventoryRepository, message_queue: MessageQueue):
        self.repository = repository
        self.message_queue = message_queue

    async def handle_order_created(self, event: OrderCreated) -> None:
        try:
            for item in event.items:
                inventory = await self.repository.get_by_product_id(item.product_id)
                
                if not inventory:
                    unavailable_event = InventoryUnavailable(
                        order_id=event.order_id,
                        product_id=item.product_id,
                        requested_quantity=item.quantity,
                        available_quantity=0
                    )
                    await self.message_queue.publish_event(unavailable_event, "inventory.unavailable")
                    return

                if inventory.quantity_available < item.quantity:
                    unavailable_event = InventoryUnavailable(
                        order_id=event.order_id,
                        product_id=item.product_id,
                        requested_quantity=item.quantity,
                        available_quantity=inventory.quantity_available
                    )
                    await self.message_queue.publish_event(unavailable_event, "inventory.unavailable")
                    return

            # All items available, reserve inventory
            for item in event.items:
                success = await self.repository.reserve_quantity(item.product_id, item.quantity)
                if success:
                    reserved_event = InventoryReserved(
                        order_id=event.order_id,
                        product_id=item.product_id,
                        quantity=item.quantity
                    )
                    await self.message_queue.publish_event(reserved_event, "inventory.reserved")
                    logger.info(f"Reserved {item.quantity} units of product {item.product_id}")

        except Exception as e:
            logger.error(f"Error handling order created event: {e}")

    async def get_inventory(self, product_id: UUID) -> Optional[InventoryItem]:
        """Get inventory for a product"""
        return await self.repository.get_by_product_id(product_id)

    async def update_inventory(self, product_id: UUID, quantity_available: int) -> Optional[InventoryItem]:
        """Update inventory quantity"""
        return await self.repository.update_quantity(product_id, quantity_available)

    async def create_inventory(self, inventory: InventoryItem) -> InventoryItem:
        """Create new inventory item"""
        return await self.repository.create(inventory)