import json

from rest_framework.exceptions import ValidationError
from rest_framework.generics import ListAPIView, CreateAPIView
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter
from rest_framework.pagination import LimitOffsetPagination

from .serializers import ProductSerializer
from .models import Product


class ProductsPagination(LimitOffsetPagination):
    default_limit = 10
    max_limit = 100


class ProductList(ListAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = (DjangoFilterBackend, SearchFilter)
    filterset_fields = ("id", "category")
    search_fields = ("name", "description")
    pagination_class = ProductsPagination

    def get_queryset(self):
        queryset = Product.objects.all()
        property_filter = self.request.query_params.get("property", None)
        if property_filter:
            try:
                # Convert the property string to a dictionary
                property_dict = json.loads(property_filter)
                params = {
                    f"property__{key}": value for key, value in property_dict.items()
                }
                queryset = queryset.filter(**params)
            except json.JSONDecodeError:
                # Handle cases where the property value is not valid JSON
                raise ValueError("Invalid JSON format for property filter")
        return queryset


class ProductCreate(CreateAPIView):
    serializer_class = ProductSerializer

    def create(self, request, *args, **kwargs):
        try:
            price = request.data.get("price")
            if price is not None and float(price) <= 0.0:
                raise ValidationError({"price": "Price must be greater than 0"})
        except ValueError:
            raise ValidationError({"price": "Invalid price format"})
        return super().create(request, *args, **kwargs)
