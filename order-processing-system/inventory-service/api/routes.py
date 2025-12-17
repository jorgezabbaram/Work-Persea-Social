from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from application.inventory_service import InventoryService
from domain.models import InventoryItem, InventoryResponse
from infrastructure.database import get_db_session
from infrastructure.repository import InventoryRepository
from infrastructure.message_queue import message_queue

router = APIRouter(prefix="/inventory", tags=["inventory"])


async def get_inventory_service(session: AsyncSession = Depends(get_db_session)) -> InventoryService:
    repository = InventoryRepository(session)
    return InventoryService(repository, message_queue)


@router.get("/{product_id}", response_model=InventoryResponse)
async def get_inventory(
    product_id: UUID,
    service: InventoryService = Depends(get_inventory_service)
) -> InventoryResponse:
    """Get inventory for a product"""
    inventory = await service.get_inventory(product_id)
    if not inventory:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found in inventory"
        )
    
    return InventoryResponse(
        id=inventory.id,
        product_id=inventory.product_id,
        quantity_available=inventory.quantity_available,
        reserved_quantity=inventory.reserved_quantity,
        created_at=inventory.created_at,
        updated_at=inventory.updated_at,
    )


@router.put("/{product_id}", response_model=InventoryResponse)
async def update_inventory(
    product_id: UUID,
    quantity_available: int,
    service: InventoryService = Depends(get_inventory_service)
) -> InventoryResponse:
    """Update inventory quantity"""
    inventory = await service.update_inventory(product_id, quantity_available)
    if not inventory:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found in inventory"
        )
    
    return InventoryResponse(
        id=inventory.id,
        product_id=inventory.product_id,
        quantity_available=inventory.quantity_available,
        reserved_quantity=inventory.reserved_quantity,
        created_at=inventory.created_at,
        updated_at=inventory.updated_at,
    )


@router.post("/", response_model=InventoryResponse, status_code=status.HTTP_201_CREATED)
async def create_inventory(
    product_id: UUID,
    quantity_available: int,
    service: InventoryService = Depends(get_inventory_service)
) -> InventoryResponse:
    """Create new inventory item"""
    inventory = InventoryItem(
        product_id=product_id,
        quantity_available=quantity_available
    )
    
    created_inventory = await service.create_inventory(inventory)
    
    return InventoryResponse(
        id=created_inventory.id,
        product_id=created_inventory.product_id,
        quantity_available=created_inventory.quantity_available,
        reserved_quantity=created_inventory.reserved_quantity,
        created_at=created_inventory.created_at,
        updated_at=created_inventory.updated_at,
    )