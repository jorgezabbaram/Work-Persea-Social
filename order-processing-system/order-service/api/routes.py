from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from application.order_service import OrderService
from domain.models import CreateOrderRequest, OrderResponse
from infrastructure.database import get_db_session
from infrastructure.repository import OrderRepository
from infrastructure.message_queue import message_queue

router = APIRouter(prefix="/orders", tags=["orders"])


async def get_order_service(session: AsyncSession = Depends(get_db_session)) -> OrderService:
    repository = OrderRepository(session)
    return OrderService(repository, message_queue)


@router.post("", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
async def create_order(
    request: CreateOrderRequest,
    service: OrderService = Depends(get_order_service)
) -> OrderResponse:
    try:
        order = await service.create_order(request)
        return OrderResponse(
            id=order.id,
            customer_id=order.customer_id,
            items=order.items,
            total_amount=order.total_amount,
            status=order.status,
            created_at=order.created_at,
            updated_at=order.updated_at,
        )
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create order: {str(e)}"
        )


@router.get("/{order_id}", response_model=OrderResponse)
async def get_order(
    order_id: UUID,
    service: OrderService = Depends(get_order_service)
) -> OrderResponse:
    order = await service.get_order(order_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    return OrderResponse(
        id=order.id,
        customer_id=order.customer_id,
        items=order.items,
        total_amount=order.total_amount,
        status=order.status,
        created_at=order.created_at,
        updated_at=order.updated_at,
    )


@router.delete("/{order_id}", response_model=OrderResponse)
async def cancel_order(
    order_id: UUID,
    reason: str = "Customer cancellation",
    service: OrderService = Depends(get_order_service)
) -> OrderResponse:
    order = await service.cancel_order(order_id, reason)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    return OrderResponse(
        id=order.id,
        customer_id=order.customer_id,
        items=order.items,
        total_amount=order.total_amount,
        status=order.status,
        created_at=order.created_at,
        updated_at=order.updated_at,
    )


@router.get("/customer/{customer_id}", response_model=List[OrderResponse])
async def list_customer_orders(
    customer_id: UUID,
    service: OrderService = Depends(get_order_service)
) -> List[OrderResponse]:
    orders = await service.list_customer_orders(customer_id)
    return [
        OrderResponse(
            id=order.id,
            customer_id=order.customer_id,
            items=order.items,
            total_amount=order.total_amount,
            status=order.status,
            created_at=order.created_at,
            updated_at=order.updated_at,
        )
        for order in orders
    ]