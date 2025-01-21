from rest_framework import serializers

from .models import Product


class ProductSerializer(serializers.ModelSerializer):
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
