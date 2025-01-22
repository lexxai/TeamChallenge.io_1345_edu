# from django.urls import path
from rest_framework.routers import DefaultRouter
from rest_framework_nested import routers

from .api_views import (
    ProductViewSet,
    ProductImageViewSet,
)

router = DefaultRouter()
router.register("", ProductViewSet, basename="product")

# Create a nested router for product images
product_router = routers.NestedDefaultRouter(router, r"", lookup="product")
product_router.register(r"images", ProductImageViewSet, basename="product-images")


urlpatterns = router.urls + product_router.urls

# urlpatterns = [
#     path("", ProductListCreateView.as_view(), name="product-list"),
#     path(
#         "<int:pk>/", ProductGetUpdateDeleteViewDetail.as_view(), name="product-detail"
#     ),
#     # path("get", ProductList.as_view()),
#     # path("new/", ProductCreate.as_view()),
# ]
