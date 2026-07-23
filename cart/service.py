from .models import Cart , CartItem
from django.db import transaction

from django.shortcuts import get_object_or_404
from catalog.models import Product
from core.exceptions import OutOfStockError


def create_cart() -> Cart:
    return Cart.objects.create() #create an empty cart object


def get_cart(cart_id) -> Cart:
    return get_object_or_404(Cart, pk = cart_id) #to retrive the detals of a particular cart

@transaction.atomic
def add_item(cart : Cart , product_id: int , quantity : int) -> CartItem:
    '''checks if the product id is existing and adds it to cart'''

    product = get_object_or_404(Product, pk = product_id , is_active = True)

    #check if the item is already present in the cart and returns it if exist or create an item if it does not exist
    item, _ = CartItem.objects.get_or_create(
        cart = cart , product = product, defaults= {"quantity":0}
    )

    #add or sub the quantity to existing quantity
    new_quantity = item.quantity + quantity

    #check if enough stock available or not, if not available just show error
    if(new_quantity > product.stock_quantity):
        raise OutOfStockError(f"Only {product.stock_quantity} units of {product.name} is currently available")
    
    #if stock available, add it to cart itam and save
    item.quantity = new_quantity
    item.save()
    return item

@transaction.atomic
def update_item(cart: Cart, product_id:int, quantity : int):
    item = get_object_or_404(CartItem , cart= cart , product_id = product_id)

    if quantity == 0:
        item.delete()
        return None
    
    if(quantity > item.product.stock_quantity):
        raise OutOfStockError(f"Only {item.product.stock_quantity} unit(s) of "
            f"'{item.product.name}' is currently available.")

    item.quantity = quantity 
    item.save()
    return None

def remove_item(cart: Cart, product_id : int) -> None:
    get_object_or_404(CartItem , cart = cart , product_id = product_id).delete()

def clear_cart(cart : Cart):
    cart.items.all().delete()