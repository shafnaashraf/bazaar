# Register your models here.
from django.contrib import admin


from .models import DiscountCode

@admin.register(DiscountCode)
class DiscountAdmin(admin.ModelAdmin):
    list_display = ["code","percent_off","is_active","valid_from","valid_until"]


