import hashlib
import json
from venv import logger

from django.core.cache import cache
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
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from django_filters import rest_framework as filters
from rest_framework_simplejwt.authentication import JWTAuthentication

from category.models import Category
from users.permissions import IsAuthenticatedOrReadOnlyWithMangers
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


@extend_schema(tags=["Products API"])
class ProductViewSet(ModelViewSet):
    # queryset = Product.objects.all()
    permission_classes = [IsAuthenticatedOrReadOnlyWithMangers]
    queryset = Product.objects.prefetch_related("images")
    serializer_class = ProductSerializer
    filter_backends = (DjangoFilterBackend, SearchFilter, OrderingFilter)
    filterset_class = ProductFilter
    pagination_class = ProductsPagination
    ordering_fields = ["name", "price", "updated_at"]
    ordering = ["-updated_at"]  # Default ordering same as on model index and ordering
    search_fields = ("name", "description")  # Used by DRF GUI and as a fallback
    cache_time_out = 60 * 15

    def get_search_fields(self, request):
        """Dynamically determine search fields based on the database backend."""
        if connection.vendor == "postgresql":
            return ("search_vector",)
        return self.search_fields

    def list(self, request, *args, **kwargs):
        # Get filters from query parameters (e.g., category, price, etc.)
        query_params = request.query_params.copy()
        query_params["offset"] = query_params.get("offset", 0)
        # Start with a base cache key
        cache_prefix = "products_"
        cache_keys = []
        # Add each query parameter to the cache key (ignore None values)
        for key, value in query_params.items():
            if value:  # Skip empty values if needed
                cache_keys.append(f"{key}_{value}")
        cache_key = "_".join(cache_keys)

        cache_key = cache_prefix + hashlib.sha256(cache_key.encode("utf-8")).hexdigest()

        # Try to get the data from cache
        cached_product_list = cache.get(cache_key)

        if cached_product_list:
            # Return cached data if available
            cached_product_list_headers = cache.get(cache_key + "_H")
            return Response(cached_product_list, headers=cached_product_list_headers)

        # Fetch data from the database (taking pagination and filters into account)
        response = super().list(request.data, *args, **kwargs)

        # Cache the serialized data of the response (after pagination and filters are applied)
        cache.set(cache_key, response.data, timeout=self.cache_time_out)
        cache.set(cache_key + "_H", response.headers, timeout=self.cache_time_out)

        return response

    def perform_create(self, serializer):
        # Create the ProductImage instance
        product = serializer.save()

        # Cache the newly created image
        cache_key = f"product_{product.pk}"
        cache.set(cache_key, product, timeout=self.cache_time_out)

    def perform_update(self, serializer):
        # Update the ProductImage instance
        product = serializer.save()

        # Update the cache with the new data
        cache_key = f"product_{product.pk}"
        cache.set(cache_key, product, timeout=self.cache_time_out)

    def retrieve(self, request, *args, **kwargs):
        """
        Overriding retrieve to check cache first before querying the database.
        """
        pk = kwargs.get("pk")
        cache_key = f"product_{pk}"

        # Try fetching from cache
        cached_product = cache.get(cache_key)
        if cached_product:
            return Response(cached_product)

        # If not found in cache, query the database
        response = super().retrieve(request, *args, **kwargs)

        # Optionally, cache the data after retrieving it from the DB
        product = response.data
        cache.set(cache_key, product, timeout=self.cache_time_out)

        return response

    def destroy(self, request, *args, **kwargs):
        response = super().destroy(request, *args, **kwargs)
        if response.status_code == 204:
            pk = kwargs["pk"]
            cache_key = f"product_{pk}"
            cache.delete(cache_key)


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
@extend_schema(tags=["Product's images API"])
class ProductImageViewSet(ModelViewSet):
    """
    Operate with the images of product by product_pk
    """

    permission_classes = [IsAuthenticatedOrReadOnlyWithMangers]
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
