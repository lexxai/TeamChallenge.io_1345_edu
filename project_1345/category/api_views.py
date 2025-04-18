from django.db.models import Prefetch
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema
from rest_framework.generics import ListAPIView

from category.models import CategorySchema, Category
from category.serializers import CategorySerializer, CategorySchemaSerializer
from language.models import CategoryTranslation, CategorySchemaTranslation
from language.utils import get_not_primary_language


@extend_schema(tags=["Category API"])
class CategoryList(ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    filterset_fields = ["id", "name", "active", "parent"]

    def get_queryset(self):
        queryset = super().get_queryset()
        lang = get_not_primary_language()
        if lang is None:
            return queryset  # No need to load translations
        return queryset.prefetch_related(
            Prefetch(
                "translations",
                queryset=CategoryTranslation.objects.select_related("language").filter(
                    language__code=lang
                ),
                to_attr="preferred_translations",
            )
        )


@extend_schema(tags=["Category API"])
class CategorySchemaList(ListAPIView):
    queryset = CategorySchema.objects.all()
    serializer_class = CategorySchemaSerializer
    filterset_fields = ["id", "category"]

    def get_queryset(self):
        queryset = super().get_queryset()
        lang = get_not_primary_language()
        if lang is None:
            return queryset  # No need to load translations
        return queryset.prefetch_related(
            Prefetch(
                "translations",
                queryset=CategorySchemaTranslation.objects.select_related(
                    "language"
                ).filter(language__code=lang),
                to_attr="preferred_translations",
            )
        )
