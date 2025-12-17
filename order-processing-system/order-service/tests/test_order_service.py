import pytest
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

from application.order_service import OrderService
from domain.models import CreateOrderRequest, OrderItem, Order, OrderStatus
from domain.events import PaymentProcessed, PaymentFailed


class TestOrderService:
    
    @pytest.fixture
    def mock_repository(self):
        return AsyncMock()
    
    @pytest.fixture
    def mock_message_queue(self):
        return AsyncMock()
    
    @pytest.fixture
    def order_service(self, mock_repository, mock_message_queue):
        return OrderService(mock_repository, mock_message_queue)
    
    @pytest.fixture
    def sample_order_request(self):
        return CreateOrderRequest(
            customer_id=uuid4(),
            items=[
                OrderItem(product_id=uuid4(), quantity=2, price=10.0),
                OrderItem(product_id=uuid4(), quantity=1, price=15.0)
            ]
        )

    async def test_create_order_success(self, order_service, mock_repository, mock_message_queue, sample_order_request):
        """Test 1: Successful order creation"""
        # Arrange
        expected_order = Order(
            id=uuid4(),
            customer_id=sample_order_request.customer_id,
            items=sample_order_request.items,
            total_amount=35.0,
            status=OrderStatus.PENDING
        )
        mock_repository.create.return_value = expected_order
        
        # Act
        result = await order_service.create_order(sample_order_request)
        
        # Assert
        assert result.customer_id == sample_order_request.customer_id
        assert result.total_amount == 35.0
        assert result.status == OrderStatus.PENDING
        mock_repository.create.assert_called_once()
        mock_message_queue.publish_event.assert_called_once()

    async def test_create_order_with_rabbitmq_mock(self, order_service, mock_repository, mock_message_queue, sample_order_request):
        """Test 2: Mocking RabbitMQ message publishing"""
        # Arrange
        expected_order = Order(
            id=uuid4(),
            customer_id=sample_order_request.customer_id,
            items=sample_order_request.items,
            total_amount=35.0,
            status=OrderStatus.PENDING
        )
        mock_repository.create.return_value = expected_order
        
        # Act
        await order_service.create_order(sample_order_request)
        
        # Assert - Verify RabbitMQ interaction
        mock_message_queue.publish_event.assert_called_once()
        call_args = mock_message_queue.publish_event.call_args
        published_event = call_args[0][0]
        routing_key = call_args[0][1]
        
        assert published_event.event_type == "OrderCreated"
        assert published_event.order_id == expected_order.id
        assert routing_key == "order.created"

    async def test_create_order_with_postgresql_mock(self, order_service, mock_repository, mock_message_queue, sample_order_request):
        """Test 3: Mocking PostgreSQL database operations"""
        # Arrange
        mock_repository.create = AsyncMock()
        expected_order = Order(
            id=uuid4(),
            customer_id=sample_order_request.customer_id,
            items=sample_order_request.items,
            total_amount=35.0,
            status=OrderStatus.PENDING
        )
        mock_repository.create.return_value = expected_order
        
        # Act
        result = await order_service.create_order(sample_order_request)
        
        # Assert - Verify database interaction
        mock_repository.create.assert_called_once()
        created_order_arg = mock_repository.create.call_args[0][0]
        
        assert isinstance(created_order_arg, Order)
        assert created_order_arg.customer_id == sample_order_request.customer_id
        assert created_order_arg.total_amount == 35.0
        assert created_order_arg.status == OrderStatus.PENDING
        assert result == expected_order

    async def test_handle_payment_processed(self, order_service, mock_repository):
        """Test handling PaymentProcessed event"""
        # Arrange
        order_id = uuid4()
        payment_id = uuid4()
        event = PaymentProcessed(
            order_id=order_id,
            payment_id=payment_id,
            amount=100.0
        )
        
        # Act
        await order_service.handle_payment_processed(event)
        
        # Assert
        mock_repository.update_status.assert_called_once_with(order_id, OrderStatus.COMPLETED)

    async def test_handle_payment_failed(self, order_service, mock_repository):
        """Test handling PaymentFailed event"""
        # Arrange
        order_id = uuid4()
        payment_id = uuid4()
        event = PaymentFailed(
            order_id=order_id,
            payment_id=payment_id,
            reason="Insufficient funds"
        )
        
        # Act
        await order_service.handle_payment_failed(event)
        
        # Assert
        mock_repository.update_status.assert_called_once_with(order_id, OrderStatus.FAILED)