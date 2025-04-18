import hashlib
import json
import logging

from django.conf import settings
from django.core.cache import cache
from django.db import connection
from django.db.models import Count, Prefetch
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
from language.models import ProductTranslation
from users.permissions import IsAuthenticatedOrReadOnlyWithMangers
from language.utils import get_not_primary_language
from .serializers import (
    ProductSerializer,
    ProductImageSerializer,
)
from .models import Product, ProductImage

logger = logging.getLogger(__name__)


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


class CustomProductsPagination(ProductsPagination):
    display_page_controls = True
    # @property
    # def display_page_controls(self):
    #     return True
    #
    # @display_page_controls.setter
    # def display_page_controls(self, value): ...
    ...


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
    cache_time_out = 60 * 60
    cache_enabled = False

    def get_queryset(self):
        queryset = super().get_queryset()
        lang = get_not_primary_language()
        if lang is None:
            logger.debug("Primary language, skip translations")
            return queryset  # No need to load translations
        return queryset.prefetch_related(
            Prefetch(
                "translations",
                queryset=ProductTranslation.objects.select_related("language").filter(
                    language__code=lang
                ),
                to_attr="preferred_translations",
            )
        )

    def get_search_fields(self, request):
        """Dynamically determine search fields based on the database backend."""
        if connection.vendor == "postgresql":
            return ("search_vector",)
        return self.search_fields

    def _configure_paginator_from_cache(self, cached_data):
        """
        Configures the paginator with cached data.
        """
        query_params = self.request.query_params
        count = int(cached_data.get("count", 0))
        limit = int(query_params.get("limit", self.paginator.default_limit))
        offset = int(query_params.get("offset", 0))

        self.paginator.display_page_controls = count > limit
        self.paginator.request = self.request
        self.paginator.limit = limit
        self.paginator.offset = offset
        self.paginator.count = count

    @staticmethod
    def clear_products_cache():
        if ProductViewSet.cache_enabled:
            # Clear all cached product lists
            cache.delete_pattern("products_*")

    @staticmethod
    def clear_product_cache(pk: int):
        # Clear all cached product lists
        if ProductViewSet.cache_enabled:
            cache.delete(ProductViewSet.get_product_cache_key(pk))
            ProductViewSet.clear_products_cache()

    @staticmethod
    def get_products_cache_key(query_params: dict) -> str:
        cache_prefix = "products_"
        cache_keys = [f"{k}_{v}" for k, v in query_params.items() if v]
        cache_key = "_".join(cache_keys)
        return cache_prefix + hashlib.sha256(cache_key.encode("utf-8")).hexdigest()

    @staticmethod
    def get_product_cache_key(pk: int) -> str:
        return f"product_{pk}"

    def set_product_cache(
        self, data: dict | str, pk: int = None, cache_key: str = None
    ):
        if self.cache_enabled is False:
            return
        if cache_key is None and pk is not None:
            cache_key = self.get_product_cache_key(pk=pk)
        if cache_key:
            cache.set(cache_key, data, timeout=self.cache_time_out)

    def get_product_cache(self, pk: int = None, cache_key: str = None) -> any:
        if self.cache_enabled is False:
            return None
        if cache_key is None and pk is not None:
            cache_key = self.get_product_cache_key(pk=pk)
        if cache_key:
            return cache.get(cache_key)

    def list(self, request, *args, **kwargs):
        cache_key = None
        if self.cache_enabled:
            cache_key = self.get_products_cache_key(request.query_params)
            cached_product_list = self.get_product_cache(cache_key=cache_key)
            if cached_product_list:
                self._configure_paginator_from_cache(cached_product_list)
                return Response(cached_product_list)
        # without cached data
        response = super().list(request.data, *args, **kwargs)
        if self.cache_enabled:
            self.set_product_cache(response.data, cache_key=cache_key)
        return response

    def perform_create(self, serializer):
        # Create the ProductImage instance
        product = serializer.save()
        if self.cache_enabled:
            # Cache the newly created image
            self.set_product_cache(product, pk=product.pk)
            self.clear_products_cache()

    def perform_update(self, serializer):
        # Update the ProductImage instance
        product = serializer.save()
        if self.cache_enabled:
            # Update the cache with the new data
            self.set_product_cache(product, pk=product.pk)
            self.clear_products_cache()

    def perform_destroy(self, instance):
        super().perform_destroy(instance)
        if self.cache_enabled:
            pk = self.kwargs["pk"]
            self.clear_product_cache(pk=pk)

    def retrieve(self, request, *args, **kwargs):
        """
        Overriding retrieve to check cache first before querying the database.
        """
        cache_key = None
        if self.cache_enabled:
            cache_key = self.get_product_cache_key(pk=kwargs.get("pk"))
            cached_product = self.get_product_cache(cache_key=cache_key)
            # Try fetching from cache
            if cached_product:
                return Response(cached_product)

        # If not found in cache, query the database
        response = super().retrieve(request, *args, **kwargs)
        if self.cache_enabled:
            # Optionally, cache the data after retrieving it from the DB
            self.set_product_cache(response.data, cache_key=cache_key)
        return response


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
        pk = self.kwargs["product_pk"]
        product = Product.objects.get(pk=pk)
        serializer.save(product=product)
        ProductViewSet.clear_product_cache(pk=pk)

    def perform_update(self, serializer):
        super().perform_update(serializer)
        pk = self.kwargs["product_pk"]
        ProductViewSet.clear_product_cache(pk=pk)

    def perform_destroy(self, instance):
        super().perform_destroy(instance)
        pk = self.kwargs["product_pk"]
        ProductViewSet.clear_product_cache(pk=pk)
