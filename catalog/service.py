import logging

from django.core.cache import cache
from django.shortcuts import get_object_or_404;

from .models import Product

logger = logging.getLogger(__name__)

PRODUCT_LIST_CACHE_KEY = "catalog:product_list"
PRODUCT_LIST_CACHE_TTL = 60 

def serialize_product(product: Product) -> dict:
    return{
        "id" : product.id,
        "category": product.category_id,
        "category_name": product.category.name,
        "name": product.name,
        "slug": product.slug,
        "description": product.description,
        "image": product.image.url if product.image else None,
        "price": str(product.price),
        "stock_quantity": product.stock_quantity,
        "is_active": product.is_active,
        "in_stock": product.in_stock,       
    }

def list_products() -> list[dict]:

    #try to check if product list in redis 
    cached = cache.get(PRODUCT_LIST_CACHE_KEY) 
    if cached is not None: #if cache has it smply return the product list
        logger.info("Product list from cache is displayed")
        return cached
    
    #No product list in cache -> query db
    logger.info("Product list cache iss - checking db")

    products = (Product.objects.select_related("category").filter(is_active = True).order_by("name"))

    payload = [serialize_product(p) for p in products]
    cache.set(PRODUCT_LIST_CACHE_KEY, payload , timeout= PRODUCT_LIST_CACHE_TTL)

    return payload

def get_product(product_id : int) -> Product:
    return get_object_or_404(Product, pk = product_id)

def create_product(data : dict) -> Product:
    product = Product.objects.create(**data)

    invalidate_cached_prodcut_list()
    return product

def update_product(product : Product, data:dict) -> Product:
    for field, value in data.items():
        setattr(product,field, value)
    product.save()
    #remove the product list
    invalidate_cached_prodcut_list()
    return product

def invalidate_cached_prodcut_list() -> None:
    cache.delete(PRODUCT_LIST_CACHE_KEY)
    logger.info("Product list cache invalidated")