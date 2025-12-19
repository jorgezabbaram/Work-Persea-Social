from datetime import datetime
from typing import List
from uuid import UUID

from pydantic import BaseModel, Field, ConfigDict

from .models import OrderItem


class DomainEvent(BaseModel):
    model_config = ConfigDict(json_encoders={UUID: str})
    
    event_id: UUID = Field(default_factory=lambda: __import__('uuid').uuid4())
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    event_type: str


class OrderCreated(DomainEvent):
    event_type: str = "OrderCreated"
    order_id: UUID
    customer_id: UUID
    items: List[OrderItem]
    total_amount: float


class OrderCancelled(DomainEvent):
    event_type: str = "OrderCancelled"
    order_id: UUID
    reason: str


class PaymentProcessed(DomainEvent):
    event_type: str = "PaymentProcessed"
    order_id: UUID
    payment_id: UUID
    amount: float


class PaymentFailed(DomainEvent):
    event_type: str = "PaymentFailed"
    order_id: UUID
    payment_id: UUID
    reason: str


class OrderConfirmed(DomainEvent):
    event_type: str = "OrderConfirmed"
    order_id: UUID
    customer_id: UUID


class OrderCompleted(DomainEvent):
    event_type: str = "OrderCompleted"
    order_id: UUID
    customer_id: UUID