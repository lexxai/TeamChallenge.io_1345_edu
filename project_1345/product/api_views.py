import json

from django.db import connection
from django_filters import FilterSet, CharFilter
from drf_spectacular.utils import extend_schema_view, extend_schema, OpenApiParameter
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.viewsets import ModelViewSet
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend


from .serializers import ProductSerializer, ProductImageSerializer
from .models import Product, ProductImage


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
    queryset = Product.objects.prefetch_related("productimage_set")
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


@extend_schema_view(
    list=extend_schema(
        parameters=[
            OpenApiParameter(
                "product_pk",
                type=int,
                location="path",
                description="ID of the product",
                required=True,
            ),
            OpenApiParameter(
                "id",
                type=int,
                location="path",
                description="ID of the image",
                required=False,
            ),
        ]
    ),
    retrieve=extend_schema(
        parameters=[
            OpenApiParameter(
                "product_pk",
                type=int,
                location="path",
                description="ID of the product",
                required=True,
            ),
            OpenApiParameter(
                "id",
                type=int,
                location="path",
                description="ID of the image",
                required=True,  # id is required for retrieve
            ),
        ]
    ),
    # create=extend_schema(
    #     parameters=[
    #         OpenApiParameter(
    #             "product_pk", type=int, description="ID of the product", required=True
    #         )
    #     ]
    # ),
    # retrieve=extend_schema(
    #     parameters=[
    #         OpenApiParameter(
    #             "product_pk", type=int, description="ID of the product", required=True
    #         ),
    #         OpenApiParameter(
    #             "id", type=int, description="ID of the image", required=False
    #         ),
    #     ]
    # ),
    # update=extend_schema(
    #     parameters=[
    #         OpenApiParameter(
    #             "product_pk", type=int, description="ID of the product", required=True
    #         ),
    #         OpenApiParameter(
    #             "id", type=int, description="ID of the image", required=False
    #         ),
    #     ]
    # ),
    # destroy=extend_schema(
    #     parameters=[
    #         OpenApiParameter(
    #             "id", type=int, description="ID of the image", required=True
    #         )
    #     ]
    # ),
)
class ProductImageViewSet(ModelViewSet):
    """
    Operate with the images of product by product_pk
    """

    serializer_class = ProductImageSerializer

    def get_queryset(self):
        # Filter images by product ID from the URL
        return ProductImage.objects.filter(product_id=self.kwargs["product_pk"])

    def perform_create(self, serializer):
        # Automatically assign the product from the URL
        product = Product.objects.get(pk=self.kwargs["product_pk"])
        serializer.save(product=product)
