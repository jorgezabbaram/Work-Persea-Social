from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class PaymentStatus(str, Enum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class Payment(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    order_id: UUID
    amount: float = Field(gt=0)
    status: PaymentStatus = PaymentStatus.PENDING
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None

    class Config:
        use_enum_values = True


class PaymentResponse(BaseModel):
    id: UUID
    order_id: UUID
    amount: float
    status: PaymentStatus
    created_at: datetime
    updated_at: Optional[datetime] = None