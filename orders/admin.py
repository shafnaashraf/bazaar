# Register your models here.
from django.contrib import admin


from .models import DiscountCode, Order, OrderItem

@admin.register(DiscountCode)
class DiscountAdmin(admin.ModelAdmin):
    list_display = ["code","percent_off","is_active","valid_from","valid_until"]


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ["id","reference","status","subtotal","discount_amount","total","discount_code","created_at"]


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ["product","product_name","order"]
    search_fields = ["order"]