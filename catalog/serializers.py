from rest_framework import serializers
from .models import Product, Category


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id","name","slug"]
        read_only_fields = ["slug"]

class ProductSerializer(serializers.ModelSerializer):

    category_name = serializers.CharField(source = "category.name", read_only = True)
    in_stock = serializers.BooleanField(read_only =True)

    class Meta:
        model = Product
        fields = [
            "id", "category", "category_name", "name", "slug", "description",
            "image","price", "stock_quantity", "is_active", "in_stock",
            "created_at", "updated_at",
        ]
        read_only_fields = ["slug", "created_at", "updated_at"]

    def validate_price(self, value):
        # DRF calls validate_<field> automatically.
        if value < 0:
            raise serializers.ValidationError("Price must be greater than zero.")
        return value