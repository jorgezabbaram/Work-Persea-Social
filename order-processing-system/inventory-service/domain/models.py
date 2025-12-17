from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class InventoryItem(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    product_id: UUID
    quantity_available: int = Field(ge=0)
    reserved_quantity: int = Field(ge=0, default=0)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None


class ReserveInventoryRequest(BaseModel):
    product_id: UUID
    quantity: int = Field(gt=0)


class InventoryResponse(BaseModel):
    id: UUID
    product_id: UUID
    quantity_available: int
    reserved_quantity: int
    created_at: datetime
    updated_at: Optional[datetime] = None