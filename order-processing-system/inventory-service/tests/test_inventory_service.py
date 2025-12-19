import pytest
from unittest.mock import AsyncMock
from uuid import uuid4
from domain.events import OrderCreated, OrderItem
from domain.models import InventoryItem
from application.inventory_service import InventoryService

@pytest.mark.asyncio
async def test_get_inventory():
    mock_repo = AsyncMock()
    mock_queue = AsyncMock()
    service = InventoryService(mock_repo, mock_queue)
    
    product_id = uuid4()
    expected_item = InventoryItem(
        product_id=product_id,
        quantity_available=10,
        reserved_quantity=0
    )
    mock_repo.get_by_product_id.return_value = expected_item
    
    item = await service.get_inventory(product_id)
    
    assert item is not None
    assert item.product_id == product_id
    mock_repo.get_by_product_id.assert_called_once_with(product_id)

@pytest.mark.asyncio
async def test_handle_order_created_reserve_success():
    mock_repo = AsyncMock()
    mock_queue = AsyncMock()
    service = InventoryService(mock_repo, mock_queue)
    
    order_id = uuid4()
    product_id = uuid4()
    quantity = 2
    
    event = OrderCreated(
        order_id=order_id,
        customer_id=uuid4(),
        items=[OrderItem(product_id=product_id, quantity=quantity, price=10.0)],
        total_amount=20.0
    )
    
    mock_repo.get_by_product_id.return_value = InventoryItem(
        product_id=product_id,
        quantity_available=5,
        reserved_quantity=0,
        id=uuid4()
    )
    mock_repo.reserve_quantity.return_value = True

    await service.handle_order_created(event)

    mock_repo.reserve_quantity.assert_called_once_with(product_id, quantity)
    mock_queue.publish_event.assert_called()

@pytest.mark.asyncio
async def test_handle_order_created_insufficient_stock():
    mock_repo = AsyncMock()
    mock_queue = AsyncMock()
    service = InventoryService(mock_repo, mock_queue)
    
    order_id = uuid4()
    product_id = uuid4()
    quantity = 100
    
    event = OrderCreated(
        order_id=order_id,
        customer_id=uuid4(),
        items=[OrderItem(product_id=product_id, quantity=quantity, price=10.0)],
        total_amount=1000.0
    )
    
    mock_repo.get_by_product_id.return_value = InventoryItem(
        product_id=product_id,
        quantity_available=10,
        reserved_quantity=0,
        id=uuid4()
    )

    await service.handle_order_created(event)

    mock_repo.reserve_quantity.assert_not_called()
    mock_queue.publish_event.assert_called()
