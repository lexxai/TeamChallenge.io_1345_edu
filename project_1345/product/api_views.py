import json

from django.db import connection
from django.db.models import Count
from django_filters import (
    FilterSet,
    CharFilter,
    BooleanFilter,
    ModelChoiceFilter,
)
from drf_spectacular.utils import extend_schema_view, extend_schema, OpenApiParameter
from rest_framework.authentication import BasicAuthentication
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.viewsets import ModelViewSet
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from django_filters import rest_framework as filters
from rest_framework_simplejwt.authentication import JWTAuthentication

from category.models import Category
from users.permissions import IsAuthenticatedOrReadOnly
from .serializers import (
    ProductSerializer,
    ProductImageSerializer,
)
from .models import Product, ProductImage


class ProductsPagination(LimitOffsetPagination):
    default_limit = 3
    max_limit = 25


class ProductFilter(FilterSet):
    # Filtering by category (select from available categories)
    category = ModelChoiceFilter(
        queryset=Category.objects.filter(active=True),
        label="Category",
        help_text="<br>Filter by product category",
    )

    active = BooleanFilter(
        field_name="active",
        label="Active",
        help_text="Filter by active status (True/False).",
    )
    owner = CharFilter(
        field_name="owner",
        lookup_expr="icontains",
        label="Owner",
        help_text="Filter by product owner.",
    )

    property = CharFilter(
        method="filter_property",
        help_text="<br>Filter by property. It JSON object. Example: {'color': 'red', 'size': 34}",
    )
    has_image = filters.BooleanFilter(
        field_name="has_image",
        method="filter_has_image",
        label="Has Image",
        help_text="<br>Filter products that have at least one image",
    )  # Use 'has_image' in query params

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

    def filter_has_image(self, queryset, name, value):
        """
        Custom filter to check if a product has at least one associated image.
        If `value=True`, filter to only products with images.
        If `value=False`, filter to only products without images.
        """
        if value:  # Filter products that have at least one image
            return queryset.annotate(image_count=Count("images")).filter(
                image_count__gt=0
            )
        elif value is False:  # Filter products that have no images
            return queryset.annotate(image_count=Count("images")).filter(image_count=0)
        return queryset  # Return the queryset unfiltered if no value is passed


class ProductViewSet(ModelViewSet):
    # queryset = Product.objects.all()
    authentication_classes = [
        BasicAuthentication,
        JWTAuthentication,
    ]  # Support both methods
    permission_classes = [IsAuthenticatedOrReadOnly]
    queryset = Product.objects.prefetch_related("images")
    serializer_class = ProductSerializer
    filter_backends = (DjangoFilterBackend, SearchFilter, OrderingFilter)
    filterset_class = ProductFilter
    pagination_class = ProductsPagination
    ordering_fields = ["name", "price", "updated_at"]
    ordering = ["-updated_at"]  # Default ordering same as on model index and ordering
    search_fields = ("name", "description")  # Used by DRF GUI and as a fallback

    def get_search_fields(self, request):
        """Dynamically determine search fields based on the database backend."""
        if connection.vendor == "postgresql":
            return ("search_vector",)
        return self.search_fields


# ----- PRODUCT IMAGE --------


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
)
class ProductImageViewSet(ModelViewSet):
    """
    Operate with the images of product by product_pk
    """

    permission_classes = [IsAuthenticatedOrReadOnly]
    serializer_class = ProductImageSerializer

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return ProductImage.objects.none()

        # Filter images by product ID from the URL
        return ProductImage.objects.filter(product_id=self.kwargs["product_pk"])

    def perform_create(self, serializer):
        # Automatically assign the product from the URL
        product = Product.objects.get(pk=self.kwargs["product_pk"])
        serializer.save(product=product)
