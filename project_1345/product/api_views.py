import json

from django_filters import FilterSet, CharFilter
from rest_framework.exceptions import ValidationError
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework.generics import ListAPIView, CreateAPIView, GenericAPIView
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter
from rest_framework.mixins import (
    ListModelMixin,
    CreateModelMixin,
    RetrieveModelMixin,
    UpdateModelMixin,
)
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


class ProductListCreateUpdateView(
    GenericAPIView,
    ListModelMixin,
    CreateModelMixin,
    RetrieveModelMixin,
    UpdateModelMixin,
):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = (DjangoFilterBackend, SearchFilter)
    filterset_class = ProductFilter
    search_fields = ("name", "description")
    pagination_class = ProductsPagination

    def get(self, request, *args, **kwargs):
        """Handle GET request (list)"""
        if "pk" in kwargs:  # Check if `pk` is in the URL
            return self.retrieve(request, *args, **kwargs)  # Retrieve a single object
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

    def put(self, request, *args, **kwargs):
        """Handle PUT request (full update)"""
        try:
            return self.update(request, *args, **kwargs)
        except DjangoValidationError as e:
            raise ValidationError(e.message_dict)

    def patch(self, request, *args, **kwargs):
        """Handle PATCH request (partial update)"""
        try:
            return self.partial_update(request, *args, **kwargs)
        except DjangoValidationError as e:
            raise ValidationError(e.message_dict)

    def get_operation_id(self):
        """Override to provide unique operation IDs for different methods."""
        if 'pk' in self.kwargs:  # This checks if the pk parameter is provided in the URL
            # For detail view actions (POST with pk, PUT, PATCH)
            if self.action == 'update':
                return 'api_v1_products_update'
            elif self.action == 'partial_update':
                return 'api_v1_products_partial_update'
            elif self.action == 'retrieve':
                return 'api_v1_products_detail'
        else:
            # For list or create actions (POST without pk)
            if self.action == 'list':
                return 'api_v1_products_list'
            elif self.action == 'create':
                return 'api_v1_products_create'
        return super().get_operation_id()
