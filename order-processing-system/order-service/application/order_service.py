from typing import List, Optional
from uuid import UUID

from domain.events import OrderCreated, OrderCancelled, PaymentProcessed, PaymentFailed
from domain.models import Order, OrderStatus, CreateOrderRequest
from infrastructure.repository import OrderRepository
from infrastructure.message_queue import MessageQueue


class OrderService:
    def __init__(self, repository: OrderRepository, message_queue: MessageQueue):
        self.repository = repository
        self.message_queue = message_queue

    async def create_order(self, request: CreateOrderRequest) -> Order:
        """Create a new order and publish OrderCreated event"""
        # Calculate total amount
        total_amount = sum(item.price * item.quantity for item in request.items)
        
        # Create order
        order = Order(
            customer_id=request.customer_id,
            items=request.items,
            total_amount=total_amount,
        )
        
        # Save to database
        created_order = await self.repository.create(order)
        
        # Publish event
        event = OrderCreated(
            order_id=created_order.id,
            customer_id=created_order.customer_id,
            items=created_order.items,
            total_amount=created_order.total_amount,
        )
        await self.message_queue.publish_event(event, "order.created")
        
        return created_order

    async def get_order(self, order_id: UUID) -> Optional[Order]:
        """Get order by ID"""
        return await self.repository.get_by_id(order_id)

    async def cancel_order(self, order_id: UUID, reason: str) -> Optional[Order]:
        """Cancel an order and publish OrderCancelled event"""
        order = await self.repository.update_status(order_id, OrderStatus.CANCELLED)
        
        if order:
            event = OrderCancelled(order_id=order_id, reason=reason)
            await self.message_queue.publish_event(event, "order.cancelled")
        
        return order

    async def handle_payment_processed(self, event: PaymentProcessed) -> None:
        """Handle PaymentProcessed event"""
        await self.repository.update_status(event.order_id, OrderStatus.COMPLETED)

    async def handle_payment_failed(self, event: PaymentFailed) -> None:
        """Handle PaymentFailed event"""
        await self.repository.update_status(event.order_id, OrderStatus.FAILED)

    async def list_customer_orders(self, customer_id: UUID) -> List[Order]:
        """List all orders for a customer"""
        return await self.repository.list_by_customer(customer_id)