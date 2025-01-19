from rest_framework import serializers

from .models import Category, CategorySchema


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = "__all__"

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["full_path"] = instance.get_full_path()
        return data


class CategorySchemaSerializer(serializers.ModelSerializer):
    class Meta:
        model = CategorySchema
        fields = "__all__"

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["full_path"] = instance.category.get_full_path()
        return data
