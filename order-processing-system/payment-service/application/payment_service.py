import asyncio
import logging
import random
from typing import Optional
from uuid import UUID

from tenacity import retry, stop_after_attempt, wait_exponential

from domain.events import InventoryReserved, PaymentProcessed, PaymentFailed
from domain.models import Payment, PaymentStatus
from infrastructure.repository import PaymentRepository
from infrastructure.message_queue import MessageQueue

logger = logging.getLogger(__name__)


class PaymentService:
    def __init__(self, repository: PaymentRepository, message_queue: MessageQueue):
        self.repository = repository
        self.message_queue = message_queue

    async def handle_inventory_reserved(self, event: InventoryReserved) -> None:
        """Handle InventoryReserved event and process payment with retry logic"""
        try:
            # Create payment record
            payment = Payment(
                order_id=event.order_id,
                amount=0.0,  # This would come from order details in real scenario
                status=PaymentStatus.PENDING
            )
            
            created_payment = await self.repository.create(payment)
            
            # Process payment with retry logic
            success = await self._process_payment_with_retry(created_payment.id)
            
            if success:
                await self.repository.update_status(created_payment.id, PaymentStatus.COMPLETED)
                
                # Publish success event
                success_event = PaymentProcessed(
                    order_id=event.order_id,
                    payment_id=created_payment.id,
                    amount=created_payment.amount
                )
                await self.message_queue.publish_event(success_event, "payment.processed")
                
            else:
                await self.repository.update_status(created_payment.id, PaymentStatus.FAILED)
                
                # Publish failure event
                failure_event = PaymentFailed(
                    order_id=event.order_id,
                    payment_id=created_payment.id,
                    reason="Payment processing failed after retries"
                )
                await self.message_queue.publish_event(failure_event, "payment.failed")
                
        except Exception as e:
            logger.error(f"Error handling inventory reserved event: {e}")
            
            # Publish failure event
            failure_event = PaymentFailed(
                order_id=event.order_id,
                payment_id=UUID('00000000-0000-0000-0000-000000000000'),
                reason=f"Payment service error: {str(e)}"
            )
            await self.message_queue.publish_event(failure_event, "payment.failed")

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        reraise=True
    )
    async def _process_payment_with_retry(self, payment_id: UUID) -> bool:
        """
        Simulate payment processing with 80% success rate and exponential backoff retry
        """
        logger.info(f"Processing payment {payment_id}")
        
        # Simulate processing time
        await asyncio.sleep(0.1)
        
        # Simulate 80% success rate
        success = random.random() < 0.8
        
        if not success:
            logger.warning(f"Payment {payment_id} failed, will retry")
            raise Exception("Payment processing failed")
        
        logger.info(f"Payment {payment_id} processed successfully")
        return True

    async def get_payment(self, payment_id: UUID) -> Optional[Payment]:
        """Get payment by ID"""
        return await self.repository.get_by_id(payment_id)

    async def get_payment_by_order(self, order_id: UUID) -> Optional[Payment]:
        """Get payment by order ID"""
        return await self.repository.get_by_order_id(order_id)