from rest_framework import serializers

from .models import Cart, CartItem


class CartItemSerializer(serializers.ModelSerializer):
    
    product_name = serializers.CharField(source = "product.name", read_only = True)
    unit_price = serializers.DecimalField(source = "product.price" , max_digits=10, decimal_places=2, read_only = True)

    line_total = serializers.DecimalField(max_digits=15, decimal_places=2, read_only =True)

    class Meta:
        model = CartItem
        fields = ["product","product_name","unit_price" , "quantity", "line_total"]


class CartSerializer(serializers.ModelSerializer):

    items = CartItemSerializer(many = True, read_only = True)
    subtotal = serializers.DecimalField(max_digits=20, decimal_places=2, read_only = True)

    item_count = serializers.IntegerField(read_only = True)

    class Meta:
        model = Cart
        fields = ["id", "items", "subtotal", "item_count"]


# Input serializers validate request bodies for writes:
class AddItemSerializer(serializers.Serializer):
    product = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1, default=1)


class UpdateItemSerializer(serializers.Serializer):
    quantity = serializers.IntegerField(min_value=0)