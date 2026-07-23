import logging
from decimal import Decimal

from django.db import transaction
from django.db.models import F

from catalog.models import Product
from catalog.service import invalidate_cached_prodcut_list
from cart import service as cart_service
from core.exceptions import EmptyCartError, InvalidDiscountError, OutOfStockError

from .models import DiscountCode, Order, OrderItem
from .tasks import send_order_confirmation

logger = logging.getLogger(__name__)


@transaction.atomic
def checkout(cart, discount_code:str |None = None):
    
    # Cart must not be empty. Read items once, sorted by product id so we
    #    always lock rows in a consistent order (prevents deadlocks).
    items = list(cart.items.select_related("product").order_by("product_id"))

    if not items:
        raise EmptyCartError()
    
    product_ids = [item.product_id for item in items]

    # Lock the product rows for this transaction. select_for_update() issues
    #    "SELECT ... FOR UPDATE", so concurrent checkouts on the same products
    #    are serialized by the DB — no overselling. (Needs PostgreSQL.)

    locked_products = {
        p.id : p
        for p in Product.objects.select_for_update()
        .filter(id__in=product_ids).order_by("id")
    }

    #check the stock against the locked quantity
    for item in items:
        product = locked_products[item.product_id]
        if item.quantity > product.stock_quantity:
            raise OutOfStockError(
                f"Only {product.stock_quantity} unit(s) of '{product.name}'is curently available.")

    subtotal = sum(
            (locked_products[item.product_id].price * item.quantity for item in items),
        start=Decimal("0.00"))
        
    #calculate the discount amount after checkig the validity details of the dicsoint
    disount = find_discount_info(discount_code)
    discount_amt = disount.discount_for(subtotal) if disount else Decimal("0.00")
    total = subtotal - discount_amt

    # rceate the order.
    order = Order.objects.create(
        subtotal=subtotal, discount_amount=discount_amt, total=total,
        discount_code=disount, status=Order.Status.PENDING)

    # Create the lines (snapshotting price paid) and reduce stock.
    order_items = []
    for item in items:
        product = locked_products[item.product_id]
        unit_price = product.price
        #add all the item related details to order
        order_items.append(OrderItem(
            order=order, product=product, product_name=product.name,
            unit_price=unit_price, quantity=item.quantity,
            line_total=unit_price * item.quantity))
        # update the remaing stock quantity
        product.stock_quantity = F("stock_quantity") - item.quantity
        product.save(update_fields=["stock_quantity"])

    OrderItem.objects.bulk_create(order_items)   # one insert for all lines

    #empty the cart and clear the cache so new product list and quantity can be displayed
    cart_service.clear_cart(cart)
    invalidate_cached_prodcut_list()
    
    # Hand confirmation to Celery — but only AFTER this transaction commits
    transaction.on_commit(lambda: send_order_confirmation.delay(order.id))

    logger.info("Checkout complete: order no= %s total= %s", order.reference, total)
    return order



def find_discount_info(code_str: str | None) -> DiscountCode | None:
    """Look up abd validate a discount code. None if not supplied; raises if bad."""
    if not code_str:
        return None
    try:
        discount = DiscountCode.objects.get(code=code_str.upper())
    except DiscountCode.DoesNotExist:
        raise InvalidDiscountError()
    if not discount.is_valid():
        raise InvalidDiscountError()
    return discount