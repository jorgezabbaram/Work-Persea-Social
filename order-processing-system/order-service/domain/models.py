from datetime import datetime
from enum import Enum
from typing import List, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class OrderStatus(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    PROCESSING = "processing"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    FAILED = "failed"


class OrderItem(BaseModel):
    product_id: UUID
    quantity: int = Field(gt=0)
    price: float = Field(gt=0)


class Order(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    customer_id: UUID
    items: List[OrderItem]
    total_amount: float = Field(gt=0)
    status: OrderStatus = OrderStatus.PENDING
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None

    class Config:
        use_enum_values = True


class CreateOrderRequest(BaseModel):
    customer_id: UUID
    items: List[OrderItem]


class OrderResponse(BaseModel):
    id: UUID
    customer_id: UUID
    items: List[OrderItem]
    total_amount: float
    status: OrderStatus
    created_at: datetime
    updated_at: Optional[datetime] = None