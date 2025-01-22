import json

from django.db import connection
from django_filters import FilterSet, CharFilter
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.viewsets import ModelViewSet
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend


from .serializers import ProductSerializer
from .models import Product


class ProductsPagination(LimitOffsetPagination):
    default_limit = 3
    max_limit = 25


class ProductFilter(FilterSet):
    property = CharFilter(method="filter_property")

    class Meta:
        model = Product
        fields = ("category", "active", "owner")

    def filter_property(self, queryset, name, value):
        try:
            property_dict = json.loads(value)
            if property_dict:
                params = {
                    f"property__{key}": value for key, value in property_dict.items()
                }
                queryset = queryset.filter(**params)
            return queryset
        except (ValueError, TypeError, json.JSONDecodeError):
            return queryset.none()


class ProductViewSet(ModelViewSet):
    # queryset = Product.objects.all()
    queryset = Product.objects.prefetch_related("images")
    serializer_class = ProductSerializer
    filter_backends = (DjangoFilterBackend, SearchFilter, OrderingFilter)
    filterset_class = ProductFilter
    pagination_class = ProductsPagination
    ordering_fields = ["name", "price", "-updated_at"]
    ordering = ["-updated_at"]  # Default ordering same as on model index and ordering
    search_fields = ("name", "description")  # Used by DRF GUI and as a fallback

    def get_search_fields(self, request):
        """Dynamically determine search fields based on the database backend."""
        if connection.vendor == "postgresql":
            return ("search_vector",)
        return self.search_fields
