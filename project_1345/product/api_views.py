import json

from django.db import connection
from django_filters import FilterSet, CharFilter
from rest_framework import status

# from drf_spectacular.types import OpenApiTypes
from rest_framework.exceptions import ValidationError
from django.core.exceptions import ValidationError as DjangoValidationError, FieldError

# from rest_framework.generics import ListAPIView, CreateAPIView
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.generics import GenericAPIView
from rest_framework.mixins import (
    ListModelMixin,
    CreateModelMixin,
    RetrieveModelMixin,
    UpdateModelMixin,
    DestroyModelMixin,
)
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

# from drf_spectacular.utils import extend_schema, extend_schema_view
# from drf_spectacular.utils import OpenApiParameter

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


# class ProductList(ListAPIView):
#     queryset = Product.objects.all()
#     serializer_class = ProductSerializer
#     filter_backends = (DjangoFilterBackend, SearchFilter)
#     filterset_class = ProductFilter
#     search_fields = ("name", "description")
#     pagination_class = ProductsPagination
#
#
# class ProductCreate(CreateAPIView):
#     serializer_class = ProductSerializer
#
#     def create(self, request, *args, **kwargs):
#         try:
#             price = request.data.get("price")
#             if price is not None and float(price) <= 0.0:
#                 raise ValidationError({"price": "Price must be greater than 0"})
#         except ValueError:
#             raise ValidationError({"price": "Invalid price format"})
#         return super().create(request, *args, **kwargs)


# @extend_schema_view(
#     list=extend_schema(exclude=True),
#     retrieve=extend_schema(exclude=True),
#     create=extend_schema(exclude=True),
#     update=extend_schema(exclude=True),
#     partial_update=extend_schema(exclude=True),
#     destroy=extend_schema(exclude=True),
# )
# class ProductListCreateView(
#     GenericAPIView,
#     ListModelMixin,
#     CreateModelMixin,
# ):
#     queryset = Product.objects.all()
#     serializer_class = ProductSerializer
#     filter_backends = (DjangoFilterBackend, SearchFilter, OrderingFilter)
#     filterset_class = ProductFilter
#     if connection.vendor == "postgresql":
#         search_fields = ("search_vector",)
#     else:
#         search_fields = ("name", "description")
#     pagination_class = ProductsPagination
#     ordering_fields = ["name", "price", "-updated_at"]
#     ordering = ["-updated_at"]  # Default ordering
#
#     def get(self, request, *args, **kwargs):
#         """Handle GET request (list or retrieve)"""
#         return self.list(request, *args, **kwargs)
#
#     def post(self, request, *args, **kwargs):
#         """Handle POST request (create)"""
#         try:
#             price = request.data.get("price")
#             if price is not None and float(price) <= 0.0:
#                 raise ValidationError({"price": "Price must be greater than 0"})
#         except ValueError:
#             raise ValidationError({"price": "Invalid price format"})
#         try:
#             return self.create(request, *args, **kwargs)
#         except DjangoValidationError as e:
#             # Convert Django's ValidationError into DRF's ValidationError
#             raise ValidationError(e.message_dict or e.message)
#
#     # def options(self, request, *args, **kwargs):
#     #     """Handle DELETE request (destroy)"""
#     #     if "pk" not in kwargs:
#     #         self.kwargs["pk"] = None
#     #     return super().options(request, *args, **kwargs)
#
#
# class ProductGetUpdateDeleteViewDetail(
#     GenericAPIView,
#     RetrieveModelMixin,
#     UpdateModelMixin,
#     DestroyModelMixin,
# ):
#     queryset = Product.objects.all()
#     serializer_class = ProductSerializer
#
#     def get(self, request, *args, **kwargs):
#         """Handle GET request (list or retrieve)"""
#         if "pk" not in kwargs:  # Check if `pk` is in the URL
#             raise ValidationError({"pk": "Primary key (pk) is required."})
#         return self.retrieve(request, *args, **kwargs)  # Retrieve a single object
#
#     # def put(self, request, *args, **kwargs):
#     #     """Handle PUT request (full update)"""
#     #     if "pk" not in kwargs:
#     #         raise ValidationError({"pk": "Primary key (pk) is required."})
#     #     try:
#     #         return self.update(request, *args, **kwargs)
#     #     except DjangoValidationError as e:
#     #         raise ValidationError(e.message_dict)
#
#     def patch(self, request, *args, **kwargs):
#         """Handle PATCH request (partial update)"""
#         if "pk" not in kwargs:
#             raise ValidationError({"pk": "Primary key (pk) is required."})
#         try:
#             return self.partial_update(request, *args, **kwargs)
#         except DjangoValidationError as e:
#             raise ValidationError(e.message_dict)
#
#     def delete(self, request, *args, **kwargs):
#         """Handle DELETE request (destroy)"""
#         if "pk" not in kwargs:
#             raise ValidationError({"pk": "Primary key (pk) is required."})
#         return self.destroy(request, *args, **kwargs)


from rest_framework.viewsets import ModelViewSet
from django.db import connection
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from .models import Product
from .serializers import ProductSerializer

# from .pagination import ProductsPagination
# from .filters import ProductFilter


class ProductViewSet(ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = (DjangoFilterBackend, SearchFilter, OrderingFilter)
    filterset_class = ProductFilter
    pagination_class = ProductsPagination
    ordering_fields = ["name", "price", "-updated_at"]
    ordering = ["-updated_at"]  # Default ordering
    search_fields = ("name", "description")  # Used by DRF GUI and as a fallback

    def get_search_fields(self, request):
        """Dynamically determine search fields based on the database backend."""
        if connection.vendor == "postgresql":
            return ("search_vector",)
        return self.search_fields
