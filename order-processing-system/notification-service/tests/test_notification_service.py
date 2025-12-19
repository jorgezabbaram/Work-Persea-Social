import pytest
from unittest.mock import AsyncMock, patch
from uuid import uuid4
from application.notification_service import NotificationService
from domain.events import OrderConfirmed, PaymentProcessed, PaymentFailed, OrderCompleted

@pytest.mark.asyncio
async def test_handle_order_confirmed():
    # Arrange
    service = NotificationService()
    event = OrderConfirmed(
        order_id=uuid4(),
        customer_id=uuid4(),
        items=[],
        total_amount=100.0,
        event_id=uuid4()
    )
    
    # Act
    with patch('application.notification_service.logger') as mock_logger:
        await service.handle_order_confirmed(event)
        
        # Assert
        assert mock_logger.info.call_count >= 1
        mock_logger.info.assert_any_call("NOTIFICATION SENT:")
        # Check that we log the right subject
        found_subject = False
        for call in mock_logger.info.call_args_list:
            if "Subject: Order Confirmed" in str(call):
                found_subject = True
        assert found_subject

@pytest.mark.asyncio
async def test_handle_payment_processed():
    # Arrange
    service = NotificationService()
    event = PaymentProcessed(
        order_id=uuid4(),
        amount=50.0,
        payment_id=uuid4()
    )
    
    # Act
    with patch('application.notification_service.logger') as mock_logger:
        await service.handle_payment_processed(event)
        
        # Assert
        assert mock_logger.info.call_count >= 1
        found_subject = False
        for call in mock_logger.info.call_args_list:
            if "Subject: Payment Successful" in str(call):
                found_subject = True
        assert found_subject
