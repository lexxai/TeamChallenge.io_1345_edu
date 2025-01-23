from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema
from rest_framework.generics import ListAPIView

from category.models import CategorySchema, Category
from category.serializers import CategorySerializer, CategorySchemaSerializer


@extend_schema(tags=["Category API"])
class CategoryList(ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    filterset_fields = ["id", "name", "active", "parent"]


@extend_schema(tags=["Category API"])
class CategorySchemaList(ListAPIView):
    queryset = CategorySchema.objects.all()
    serializer_class = CategorySchemaSerializer
    filterset_fields = ["id", "category"]
