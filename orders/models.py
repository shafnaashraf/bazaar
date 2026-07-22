from django.db import models
import uuid
from decimal import Decimal

from django.core.validators import MaxValueValidator, MinValueValidator

from django.db import models
from django.utils import timezone
from catalog.models import Product

class DiscountCode(models.Model):

    code = models.CharField(max_length=40, unique=True)

    percent_off = models.DecimalField(max_digits=5, decimal_places=2, validators=[MinValueValidator(Decimal("0")),MaxValueValidator(Decimal("80"))],)

    is_active = models.BooleanField(default=True)

    valid_from = models.DateTimeField(null=True, blank=True)
    valid_until = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.code} (-{self.percent_off}%)"
    
    def save(self, *args, **kwargs):
        self.code = self.code.upper()
        super().save(*args, **kwargs)

    def is_valid(self , when = None) -> bool:
        when = when or timezone.now()
        if not self.is_active:
            return False
        if self.valid_from and when < self.valid_from:
            return False
        if self.valid_until and when > self.valid_until:
            return False
        return True
    
    def discount_for(self, subtotal: Decimal) -> Decimal:
        return (subtotal * (self.percent_off / Decimal("100"))).quantize(Decimal("0.01"))
    


class Order(models.Model):
    class Status(models.TextChoices):        # Django's enum: DB value, human label
        PENDING = "PENDING", "Pending"       # created; follow-up not done yet
        CONFIRMED = "CONFIRMED", "Confirmed" # Celery task finished

    # Public, non-sequential id to show customers (don't expose the integer PK).
    reference = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)

    # Money snapshot: total = subtotal - discount_amount.
    subtotal = models.DecimalField(max_digits=12, decimal_places=2)
    discount_amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    total = models.DecimalField(max_digits=12, decimal_places=2)

    # SET_NULL keeps the order intact even if the code is later deleted.
    discount_code = models.ForeignKey(DiscountCode, null=True, blank=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]   # newest first

    def __str__(self) -> str:
        return f"Order {self.reference} ({self.status})"


class OrderItem(models.Model):
    """A frozen line: what was bought and the price paid."""
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    # SET_NULL so deleting a product doesn't erase order history.
    product = models.ForeignKey(Product, null=True, on_delete=models.SET_NULL)

    product_name = models.CharField(max_length=200)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)   # price paid per unit
    quantity = models.PositiveIntegerField()
    line_total = models.DecimalField(max_digits=12, decimal_places=2)

    def __str__(self) -> str:
        return f"{self.quantity} x {self.product_name} @ {self.unit_price}"
