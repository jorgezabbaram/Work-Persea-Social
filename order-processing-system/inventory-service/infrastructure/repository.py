from typing import Optional
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from domain.models import InventoryItem
from .database import InventoryItem as InventoryModel


class InventoryRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_product_id(self, product_id: UUID) -> Optional[InventoryItem]:
        result = await self.session.execute(
            select(InventoryModel).where(InventoryModel.product_id == product_id)
        )
        inventory_model = result.scalar_one_or_none()
        return self._to_domain(inventory_model) if inventory_model else None

    async def create(self, inventory: InventoryItem) -> InventoryItem:
        inventory_model = InventoryModel(
            id=inventory.id,
            product_id=str(inventory.product_id),
            quantity=inventory.quantity_available,
            reserved_quantity=inventory.reserved_quantity,
        )
        self.session.add(inventory_model)
        await self.session.commit()
        await self.session.refresh(inventory_model)
        return self._to_domain(inventory_model)

    async def reserve_quantity(self, product_id: UUID, quantity: int) -> bool:
        result = await self.session.execute(
            select(InventoryModel).where(InventoryModel.product_id == product_id)
        )
        inventory_model = result.scalar_one_or_none()
        
        if not inventory_model or inventory_model.quantity < quantity:
            return False

        await self.session.execute(
            update(InventoryModel)
            .where(InventoryModel.product_id == product_id)
            .values(
                quantity=InventoryModel.quantity - quantity,
                reserved_quantity=InventoryModel.reserved_quantity + quantity
            )
        )
        await self.session.commit()
        return True

    async def update_quantity(self, product_id: UUID, quantity_available: int) -> Optional[InventoryItem]:
        await self.session.execute(
            update(InventoryModel)
            .where(InventoryModel.product_id == product_id)
            .values(quantity=quantity_available)
        )
        await self.session.commit()
        return await self.get_by_product_id(product_id)

    def _to_domain(self, model: InventoryModel) -> InventoryItem:
        return InventoryItem(
            id=model.id,
            product_id=model.product_id,
            quantity_available=model.quantity,
            reserved_quantity=model.reserved_quantity,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )