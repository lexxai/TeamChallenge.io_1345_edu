from rest_framework.generics import ListAPIView

from category.models import CategorySchema, Category
from category.serializers import CategorySerializer, CategorySchemaSerializer


class CategoryList(ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class CategorySchemaList(ListAPIView):
    queryset = CategorySchema.objects.all()
    serializer_class = CategorySchemaSerializer
