from datetime import datetime
from typing import List
from uuid import UUID

from pydantic import BaseModel, Field


class DomainEvent(BaseModel):
    event_id: UUID = Field(default_factory=lambda: __import__('uuid').uuid4())
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    event_type: str


class OrderItem(BaseModel):
    product_id: UUID
    quantity: int
    price: float


class OrderCreated(DomainEvent):
    event_type: str = "OrderCreated"
    order_id: UUID
    customer_id: UUID
    items: List[OrderItem]
    total_amount: float


class InventoryReserved(DomainEvent):
    event_type: str = "InventoryReserved"
    order_id: UUID
    product_id: UUID
    quantity: int


class InventoryUnavailable(DomainEvent):
    event_type: str = "InventoryUnavailable"
    order_id: UUID
    product_id: UUID
    requested_quantity: int
    available_quantity: int