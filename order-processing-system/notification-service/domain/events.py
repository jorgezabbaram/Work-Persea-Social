from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class DomainEvent(BaseModel):
    event_id: UUID = Field(default_factory=lambda: __import__('uuid').uuid4())
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    event_type: str


class OrderConfirmed(DomainEvent):
    event_type: str = "OrderConfirmed"
    order_id: UUID
    customer_id: UUID


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


class OrderCompleted(DomainEvent):
    event_type: str = "OrderCompleted"
    order_id: UUID
    customer_id: UUID