import json
from typing import List, Optional
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from domain.models import Order, OrderStatus
from .database import OrderModel


from pydantic import TypeAdapter
from domain.models import OrderItem

class OrderRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, order: Order) -> Order:
        adapter = TypeAdapter(List[OrderItem])
        items_json = adapter.dump_json(order.items).decode('utf-8')
        
        order_model = OrderModel(
            id=order.id,
            customer_id=order.customer_id,
            items=items_json,
            total_amount=order.total_amount,
            status=order.status,
        )
        self.session.add(order_model)
        await self.session.commit()
        await self.session.refresh(order_model)
        return self._to_domain(order_model)

    async def get_by_id(self, order_id: UUID) -> Optional[Order]:
        result = await self.session.execute(
            select(OrderModel).where(OrderModel.id == order_id)
        )
        order_model = result.scalar_one_or_none()
        return self._to_domain(order_model) if order_model else None

    async def update_status(self, order_id: UUID, status: OrderStatus) -> Optional[Order]:
        await self.session.execute(
            update(OrderModel)
            .where(OrderModel.id == order_id)
            .values(status=status)
        )
        await self.session.commit()
        return await self.get_by_id(order_id)

    async def list_by_customer(self, customer_id: UUID) -> List[Order]:
        result = await self.session.execute(
            select(OrderModel).where(OrderModel.customer_id == customer_id)
        )
        order_models = result.scalars().all()
        return [self._to_domain(model) for model in order_models]

    def _to_domain(self, model: OrderModel) -> Order:
        from domain.models import OrderItem
        
        items_data = json.loads(model.items)
        items = [OrderItem(**item) for item in items_data]
        
        return Order(
            id=model.id,
            customer_id=model.customer_id,
            items=items,
            total_amount=model.total_amount,
            status=model.status,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )