from drf_spectacular.utils import extend_schema_field
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
    name = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = "__all__"

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["full_path"] = instance.get_full_path()
        return data

    def _get_translation(self, obj):
        # `preferred_translations` is set by Prefetch in get_queryset()
        return (
            obj.preferred_translations[0]
            if hasattr(obj, "preferred_translations") and obj.preferred_translations
            else None
        )

    @extend_schema_field({"type": "string"})
    def get_name(self, obj):
        translation = self._get_translation(obj)
        name = translation.name if translation and translation.name else obj.name
        return name


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
        # Replace schema if translation exists
        translation = self._get_translation(instance)
        if translation and translation.schema:
            data["schema"] = translation.schema
        data["full_path"] = instance.category.get_full_path()
        return data

    def _get_translation(self, obj):
        # `preferred_translations` is set by Prefetch in get_queryset()
        return (
            obj.preferred_translations[0]
            if hasattr(obj, "preferred_translations") and obj.preferred_translations
            else None
        )
