import logging
import time

from celery import shared_task

from .models import Order
logger = logging.getLogger(__name__)
from django.core.mail import send_mail
from django.conf import settings


def build_confirmation_email(order):
    items = order.items.all()

    # --- plain-text version (fallback) ---
    lines = [f"  {it.quantity} x {it.product_name}  —  AED {it.line_total}" for it in items]
    text = (
        f"Thanks for your order!\n\n"
        f"Order reference: {order.reference}\n"
        f"Status: {order.get_status_display()}\n\n"
        f"Items:\n" + "\n".join(lines) + "\n\n"
        f"Subtotal:  AED {order.subtotal}\n"
        f"Discount:  -AED {order.discount_amount}\n"
        f"Total:     AED {order.total}\n\n"
        f"— Bazaar"
    )

    # --- HTML version ---
    rows = "".join(
        f"""<tr>
              <td style="padding:8px 0;border-bottom:1px solid #eee;">{it.product_name}</td>
              <td style="padding:8px 0;border-bottom:1px solid #eee;text-align:center;">{it.quantity}</td>
              <td style="padding:8px 0;border-bottom:1px solid #eee;text-align:right;">AED {it.line_total}</td>
            </tr>"""
        for it in items
    )
    html = f"""
    <div style="font-family:system-ui,Arial,sans-serif;max-width:520px;margin:auto;color:#0f172a;">
      <div style="background:#0f766e;color:#fff;padding:20px 24px;border-radius:12px 12px 0 0;">
        <h1 style="margin:0;font-size:22px;">Order confirmed 🎉</h1>
        <p style="margin:6px 0 0;opacity:.85;font-size:13px;">Reference: {order.reference}</p>
      </div>
      <div style="border:1px solid #e2e8f0;border-top:0;padding:24px;border-radius:0 0 12px 12px;">
        <p style="margin-top:0;">Thanks for shopping with Bazaar! Here's your summary:</p>
        <table style="width:100%;border-collapse:collapse;font-size:14px;">
          <thead>
            <tr style="color:#64748b;text-align:left;font-size:12px;">
              <th style="padding-bottom:6px;">Item</th>
              <th style="padding-bottom:6px;text-align:center;">Qty</th>
              <th style="padding-bottom:6px;text-align:right;">Total</th>
            </tr>
          </thead>
          <tbody>{rows}</tbody>
        </table>
        <table style="width:100%;margin-top:16px;font-size:14px;">
          <tr><td style="color:#64748b;">Subtotal</td><td style="text-align:right;">AED {order.subtotal}</td></tr>
          <tr><td style="color:#64748b;">Discount</td><td style="text-align:right;color:#16a34a;">-AED {order.discount_amount}</td></tr>
          <tr style="font-weight:700;font-size:16px;">
            <td style="padding-top:8px;border-top:2px solid #0f172a;">Total</td>
            <td style="padding-top:8px;border-top:2px solid #0f172a;text-align:right;color:#0f766e;">AED {order.total}</td>
          </tr>
        </table>
        <p style="color:#94a3b8;font-size:12px;margin-top:24px;">You're receiving this because you placed an order on Bazaar.</p>
      </div>
    </div>
    """
    return text, html

@shared_task(bind = True, max_retries = 3 , default_retry_delay = 5)
def send_order_confirmation(self, order_id : int):
    try: 
        order = Order.objects.get(pk = order_id)
    except Order.DoesNotExist:
        logger.error(f"send_order_confirmation: order no : {order_id} is not foun ")
        return
    
    logger.info(f"Sending confirmation for order no : {order_id}")
    try:
        text, html = build_confirmation_email(order)
        send_mail(
            subject=f"Order {order.reference} confirmed 🎉",
            message=text,                    # plain-text fallback
            html_message=html,               # the pretty version
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[settings.ORDER_CONFIRMATION_TO],
            fail_silently=False,
        )
    except Exception as exc:
        logger.warning(f"Email failed for order {order_id}, retrying: {exc}")
        raise self.retry(exc=exc)

    order.status = Order.Status.CONFIRMED
    order.save(update_fields=["status"])
    logger.info("Order is confirmed")
    return str(order.reference)