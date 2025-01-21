from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from .models import Product


@extend_schema_field({"type": "string", "format": "decimal", "example": "10.00"})
class CustomDecimalField(serializers.DecimalField): ...


class MultiTypeField(serializers.Field):
    """
    Custom field to support multiple value types: str, int, float, bool.
    """

    def to_representation(self, value):
        # Return the value as-is for serialization
        return value

    def to_internal_value(self, data):
        # Validate multiple types
        if isinstance(data, (str, int, float, bool)):
            return data
        raise serializers.ValidationError(
            "Value must be of type 'str', 'int', 'float', or 'bool'."
        )


@extend_schema_field(
    {
        "oneOf": [
            {"type": "string"},
            {"type": "integer"},
            {"type": "number"},
            {"type": "boolean"},
        ]
    }
)
class AnnotatedMultiTypeField(MultiTypeField): ...


class ProductSerializer(serializers.ModelSerializer):
    property = serializers.DictField(
        child=AnnotatedMultiTypeField(),
        help_text="Key-value pairs where key is string and values can be 'str', 'int', 'float', or 'bool'. Example: {'color': 'red', 'size': 34}",
    )
    price = CustomDecimalField(max_digits=10, decimal_places=2)

    class Meta:
        model = Product
        fields = (
            "id",
            "name",
            "description",
            "owner",
            "price",
            "category",
            "property",
            "created_at",
            "updated_at",
            "active",
        )

    # def to_representation(self, instance):
    #     data = super().to_representation(instance)
    #     return data
