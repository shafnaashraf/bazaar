import logging
import time

from celery import shared_task

from .models import Order
logger = logging.getLogger(__name__)
from django.core.mail import send_mail
from django.conf import settings


@shared_task(bind = True, max_retries = 3 , default_retry_delay = 5)
def send_order_confirmation(self, order_id : int):
    try: 
        order = Order.objects.get(pk = order_id)
    except Order.DoesNotExist:
        logger.error(f"send_order_confirmation: order no : {order_id} is not foun ")
        return
    
    logger.info(f"Sending confirmation for order no : {order_id}")
    try:
         send_mail(
            subject=f"Order {order.reference} confirmed",
            message=f"Thanks! Your order total is AED {order.total}.",
            from_email=settings.DEFAULT_FROM_EMAIL,      # sender from settings
            recipient_list=[settings.ORDER_CONFIRMATION_TO],  # receiver from settings
            fail_silently=False,
        )
    except Exception as exc:
        logger.warning(f"Email failed for order {order_id}, retrying: {exc}")
        raise self.retry(exc=exc)

    order.status = Order.Status.CONFIRMED
    order.save(update_fields=["status"])
    logger.info("Order is confirmed")
    return str(order.reference)