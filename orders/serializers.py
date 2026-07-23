from rest_framework import serializers

from .models import Order, OrderItem


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ["product", "product_name", "unit_price", "quantity", "line_total"]


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)

    class Meta:
        model = Order
        fields = ["reference", "status", "status_display", "subtotal",
                  "discount_amount", "total", "items", "created_at"]


class CheckoutSerializer(serializers.Serializer):
    """Body for POST /api/checkout/: {"cart": "<uuid>", "discount_code": "WELCOME10"}"""
    cart = serializers.UUIDField()
    discount_code = serializers.CharField(required=False, allow_blank=True)