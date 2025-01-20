import json

from django_filters import FilterSet, CharFilter
from rest_framework.exceptions import ValidationError
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework.generics import ListAPIView, CreateAPIView, GenericAPIView
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter
from rest_framework.mixins import ListModelMixin, CreateModelMixin
from rest_framework.pagination import LimitOffsetPagination

from .serializers import ProductSerializer
from .models import Product


class ProductsPagination(LimitOffsetPagination):
    default_limit = 3
    max_limit = 25


class ProductFilter(FilterSet):
    property = CharFilter(method="filter_property")

    class Meta:
        model = Product
        fields = ("id", "category", "active", "owner")

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


class ProductList(ListAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = (DjangoFilterBackend, SearchFilter)
    filterset_class = ProductFilter
    search_fields = ("name", "description")
    pagination_class = ProductsPagination


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


class ProductListCreateView(GenericAPIView, ListModelMixin, CreateModelMixin):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = (DjangoFilterBackend, SearchFilter)
    filterset_class = ProductFilter
    search_fields = ("name", "description")
    pagination_class = ProductsPagination

    def get(self, request, *args, **kwargs):
        """Handle GET request (list)"""
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        """Handle POST request (create)"""
        try:
            price = request.data.get("price")
            if price is not None and float(price) <= 0.0:
                raise ValidationError({"price": "Price must be greater than 0"})
        except ValueError:
            raise ValidationError({"price": "Invalid price format"})
        try:
            return self.create(request, *args, **kwargs)
        except DjangoValidationError as e:
            # Convert Django's ValidationError into DRF's ValidationError
            raise ValidationError(e.message_dict or e.message)
