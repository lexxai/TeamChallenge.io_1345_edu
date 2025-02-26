from rest_framework import serializers
from .models import ProductTranslation


class ProductTranslationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductTranslation
        fields = ("language_code", "name", "description")
