from django.db import models

import uuid
from decimal import Decimal

from catalog.models import Product


class Cart(models.Model):

    id = models.UUIDField(primary_key=True, default= uuid.uuid4 , editable= False)
    created_at = models.DateTimeField(auto_now_add= True)
    updated_at = models.DateTimeField(auto_now=True)


    def __str__(self) -> str:
        return f"Cart {self.id}"
    
    @property
    def subtotal(self) -> Decimal:
        '''Computes the total based the cart items'''
        return sum((item.line_total for item in self.items.all()),
               start = Decimal("0.00"))
    
    @property
    def item_count(self) ->int:
        ''' calculate the total number of items in the cart'''
        return (sum(item.quantity for item in self.items.all()))

class CartItem(models.Model):

    cart = models.ForeignKey(Cart , on_delete= models.CASCADE , related_name= "items")
    product = models.ForeignKey(Product, on_delete =models.PROTECT)
    quantity = models.PositiveBigIntegerField(default=1)

    class Meta:
        #an item should be added only once for a particular cart number, if we add again only the quantity should be incremented/decreemented
        constraints = [
            models.UniqueConstraint(fields=["cart","product"],
                                    name="unique_product_per_cart")
        ]
    
    def __str__(self):
        return f"{self.quantity} * {self.product.name}"
    
    @property
    def line_total(self) -> Decimal :
        '''computes the total price per product in the cart , example cost of 3 phones = cost of 1 phone * 3'''
        return(self.product.price * self.quantity)
# Create your models here.
