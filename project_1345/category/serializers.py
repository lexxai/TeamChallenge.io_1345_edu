from rest_framework import serializers

from .models import Category, CategorySchema


# Define a custom serializer for the JSON schema
class PropertySchemaSerializer(serializers.Serializer):
    type = serializers.ChoiceField(
        choices=["str", "int", "float", "bool"],
        help_text="Type of the value (str, int, float, bool)",
    )
    required = serializers.BooleanField(help_text="Indicates if the field is required")


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = "__all__"

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["full_path"] = instance.get_full_path()
        return data


class CategorySchemaSerializer(serializers.ModelSerializer):
    schema = serializers.DictField(
        child=PropertySchemaSerializer(),
        help_text="Schema: {property_name: {type: 'str|int|float|bool', required: bool}}",
    )

    class Meta:
        model = CategorySchema
        fields = "__all__"

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["full_path"] = instance.category.get_full_path()
        return data
