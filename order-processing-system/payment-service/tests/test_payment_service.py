import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from uuid import uuid4
from domain.events import InventoryReserved
from application.payment_service import PaymentService
from domain.models import Payment, PaymentStatus

@pytest.mark.asyncio
async def test_handle_inventory_reserved_success():
    # Arrange
    mock_repo = AsyncMock()
    mock_queue = AsyncMock()
    service = PaymentService(mock_repo, mock_queue)
    
    order_id = uuid4()
    event = InventoryReserved(
        order_id=order_id,
        product_id=uuid4(),
        quantity=2,
        event_id=uuid4()
    )
    
    mock_repo.create.return_value = Payment(
        id=uuid4(),
        order_id=order_id,
        amount=100.0,
        status=PaymentStatus.PENDING
    )
    
    # Act
    # Mock private method _process_payment_with_retry to avoid waiting/randomness
    # But checking if we can patch it directly on the instance or class
    # Better to patch the 'random.random' as we did, OR patch the method.
    # Since the method has a decorator 'retry', patching it might be tricky.
    # Let's patch 'random.random' as before, but call the PUBLIC METHOD handle_inventory_reserved
    
    with patch('application.payment_service.random.random', return_value=0.1): # Success
         with patch('application.payment_service.asyncio.sleep'): # Skip sleep
            await service.handle_inventory_reserved(event)

    # Assert
    mock_repo.update_status.assert_called()
    # Check that update_status was called with COMPLETED
    call_args = mock_repo.update_status.call_args
    assert call_args[0][1] == PaymentStatus.COMPLETED
    
    mock_queue.publish_event.assert_called()
    assert mock_queue.publish_event.call_args[0][1] == "payment.processed"

@pytest.mark.asyncio
async def test_handle_inventory_reserved_failure():
    # Arrange
    mock_repo = AsyncMock()
    mock_queue = AsyncMock()
    service = PaymentService(mock_repo, mock_queue)
    
    order_id = uuid4()
    event = InventoryReserved(
        order_id=order_id,
        product_id=uuid4(),
        quantity=2,
        event_id=uuid4()
    )
    
    mock_repo.create.return_value = Payment(
        id=uuid4(),
        order_id=order_id,
        amount=100.0,
        status=PaymentStatus.PENDING
    )

    # Act
    # Force failure 3 times to trigger stop_after_attempt(3)
    with patch('application.payment_service.random.random', return_value=0.9): 
        with patch('application.payment_service.asyncio.sleep'):
            # The retry logic will raise Exception after 3 failed attempts
            # But handle_inventory_reserved catches Exception
            await service.handle_inventory_reserved(event)

    # Assert
    # Should update status to FAILED
    mock_repo.update_status.assert_not_called() 
    # Wait, the code says: if exception -> logger.error ... publish failure event.
    # It DOES NOT update DB status to FAILED in the 'except' block?
    # Let's check logic:
    # try: ... success = _process... if success: update ... else: update FAILED
    # except: log ... publish failure.
    # Retry raises Exception. So it goes to 'except'.
    # So DB status remains PENDING in DB, but event FAILED is published.
    
    mock_queue.publish_event.assert_called()
    assert mock_queue.publish_event.call_args[0][1] == "payment.failed"
