from typing import Optional
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from domain.models import Payment, PaymentStatus
from .database import Payment as PaymentModel


class PaymentRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, payment: Payment) -> Payment:
        payment_model = PaymentModel(
            id=payment.id,
            order_id=payment.order_id,
            amount=payment.amount,
            status=payment.status,
        )
        self.session.add(payment_model)
        await self.session.commit()
        await self.session.refresh(payment_model)
        return self._to_domain(payment_model)

    async def get_by_id(self, payment_id: UUID) -> Optional[Payment]:
        result = await self.session.execute(
            select(PaymentModel).where(PaymentModel.id == payment_id)
        )
        payment_model = result.scalar_one_or_none()
        return self._to_domain(payment_model) if payment_model else None

    async def get_by_order_id(self, order_id: UUID) -> Optional[Payment]:
        result = await self.session.execute(
            select(PaymentModel).where(PaymentModel.order_id == order_id)
        )
        payment_model = result.scalar_one_or_none()
        return self._to_domain(payment_model) if payment_model else None

    async def update_status(self, payment_id: UUID, status: PaymentStatus) -> Optional[Payment]:
        await self.session.execute(
            update(PaymentModel)
            .where(PaymentModel.id == payment_id)
            .values(status=status)
        )
        await self.session.commit()
        return await self.get_by_id(payment_id)

    def _to_domain(self, model: PaymentModel) -> Payment:
        return Payment(
            id=model.id,
            order_id=model.order_id,
            amount=model.amount,
            status=model.status,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )