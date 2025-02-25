from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers


@extend_schema_field({"type": "string", "format": "decimal", "example": "10.00"})
class CustomDecimalField(serializers.DecimalField): ...


class CartItemSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1)
    price = CustomDecimalField(max_digits=10, decimal_places=2, required=False)


class CartContentSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    product_name = serializers.CharField(max_length=255)
    quantity = serializers.IntegerField(min_value=1)
    price = CustomDecimalField(max_digits=10, decimal_places=2)
    total_price = CustomDecimalField(max_digits=10, decimal_places=2)


class CartUpdateSerializer(serializers.Serializer):
    quantity = serializers.IntegerField(min_value=1, required=False)
    price = CustomDecimalField(max_digits=10, decimal_places=2, required=False)
