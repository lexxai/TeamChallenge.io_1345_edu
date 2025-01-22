from django.core.exceptions import FieldError
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from category.models import CategorySchema
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


class ProductSerializer0(serializers.ModelSerializer):
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
    #     return data["id"]


class ProductSerializer(serializers.ModelSerializer):
    property = serializers.DictField(
        child=AnnotatedMultiTypeField(),
        help_text="Key-value pairs where key is string and values can be 'str', 'int', 'float', or 'bool'. Example: {'color': 'red', 'size': 34}",
    )
    price = CustomDecimalField(max_digits=10, decimal_places=2)

    class Meta:
        model = Product
        fields = "__all__"

    def validate(self, data):
        # Perform schema validation
        category = data.get("category")
        property_data = data.get("property")

        if not category:
            raise ValidationError({"category": "Category is required."})

        # Get the schema for the given category
        category_schema = CategorySchema.objects.filter(category=category).first()
        if not category_schema:
            raise ValidationError({"category": "Invalid category schema."})

        # Check property data against the schema
        if property_data:
            for key, value in property_data.items():
                expected_type = category_schema.get_property_type(key)
                if not expected_type:
                    raise ValidationError(
                        {key: f"Property '{key}' is not defined in the schema."}
                    )
                if expected_type == "str" and not isinstance(value, str):
                    raise ValidationError(
                        {key: f"Property '{key}' must be of type 'str'."}
                    )
                elif expected_type == "int" and not isinstance(value, int):
                    raise ValidationError(
                        {key: f"Property '{key}' must be of type 'int'."}
                    )
                elif expected_type == "float" and not isinstance(value, float):
                    raise ValidationError(
                        {key: f"Property '{key}' must be of type 'float'."}
                    )
                elif expected_type == "bool" and not isinstance(value, bool):
                    raise ValidationError(
                        {key: f"Property '{key}' must be of type 'bool'."}
                    )

        # Check for required properties
        required_properties = [
            key
            for key, prop in category_schema.schema.items()
            if isinstance(prop, dict) and prop.get("required", False)
        ]
        for req_property in required_properties:
            if not property_data or req_property not in property_data:
                raise ValidationError(
                    {
                        req_property: f"Property '{req_property}' is required but not provided."
                    }
                )

        return data

    def save(self, **kwargs):
        # Perform any pre-save validation here
        instance = self.instance  # Get the model instance
        # Perform model-level validation (custom checks)
        if instance and not instance.name:
            raise ValidationError("Product name is required.")
        try:
            # Call the model's save method
            super().save(**kwargs)
        except FieldError as e:
            # Catch the FieldError raised by the model and re-raise it
            raise ValidationError(str(e))
        return self.instance
