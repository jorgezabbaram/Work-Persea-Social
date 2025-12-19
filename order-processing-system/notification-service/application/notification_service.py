import logging
from typing import Dict, Any

from domain.events import OrderConfirmed, PaymentProcessed, PaymentFailed, OrderCompleted

logger = logging.getLogger(__name__)


class NotificationService:
    def __init__(self):
        self.notifications = []

    def get_notifications(self) -> list:
        return self.notifications

    async def handle_order_confirmed(self, event: OrderConfirmed) -> None:
        await self._send_notification(
            event.customer_id,
            "Order Confirmed",
            f"Your order {event.order_id} has been confirmed and is being processed."
        )

    async def handle_payment_processed(self, event: PaymentProcessed) -> None:
        await self._send_notification(
            None,
            "Payment Successful",
            f"Payment for order {event.order_id} has been processed successfully. Amount: ${event.amount}"
        )

    async def handle_payment_failed(self, event: PaymentFailed) -> None:
        await self._send_notification(
            None,
            "Payment Failed",
            f"Payment for order {event.order_id} failed. Reason: {event.reason}"
        )

    async def handle_order_completed(self, event: OrderCompleted) -> None:
        await self._send_notification(
            event.customer_id,
            "Order Completed",
            f"Your order {event.order_id} has been completed successfully!"
        )

    async def _send_notification(self, customer_id: str, subject: str, message: str) -> None:
        logger.info(f"NOTIFICATION SENT:")
        logger.info(f"  Customer: {customer_id}")
        logger.info(f"  Subject: {subject}")
        logger.info(f"  Message: {message}")
        
        self.notifications.append({
            "customer_id": customer_id,
            "subject": subject,
            "message": message,
            "timestamp": "2024-01-01T00:00:00Z"
        })
        
    async def send_custom_notification(self, customer_id: str, subject: str, message: str) -> Dict[str, Any]:
        await self._send_notification(customer_id, subject, message)
        return {
            "status": "sent",
            "customer_id": customer_id,
            "subject": subject,
            "timestamp": "2024-01-01T00:00:00Z"
        }