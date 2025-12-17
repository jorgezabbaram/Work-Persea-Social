from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from application.payment_service import PaymentService
from domain.models import PaymentResponse
from infrastructure.database import get_db_session
from infrastructure.repository import PaymentRepository
from infrastructure.message_queue import message_queue

router = APIRouter(prefix="/payments", tags=["payments"])


async def get_payment_service(session: AsyncSession = Depends(get_db_session)) -> PaymentService:
    repository = PaymentRepository(session)
    return PaymentService(repository, message_queue)


@router.get("/{payment_id}", response_model=PaymentResponse)
async def get_payment(
    payment_id: UUID,
    service: PaymentService = Depends(get_payment_service)
) -> PaymentResponse:
    """Get payment by ID"""
    payment = await service.get_payment(payment_id)
    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found"
        )
    
    return PaymentResponse(
        id=payment.id,
        order_id=payment.order_id,
        amount=payment.amount,
        status=payment.status,
        created_at=payment.created_at,
        updated_at=payment.updated_at,
    )


@router.get("/order/{order_id}", response_model=PaymentResponse)
async def get_payment_by_order(
    order_id: UUID,
    service: PaymentService = Depends(get_payment_service)
) -> PaymentResponse:
    """Get payment by order ID"""
    payment = await service.get_payment_by_order(order_id)
    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found for this order"
        )
    
    return PaymentResponse(
        id=payment.id,
        order_id=payment.order_id,
        amount=payment.amount,
        status=payment.status,
        created_at=payment.created_at,
        updated_at=payment.updated_at,
    )