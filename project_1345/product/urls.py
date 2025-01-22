from django.urls import path
from rest_framework.routers import DefaultRouter

from .api_views import (
    # ProductListCreateView,
    # ProductGetUpdateDeleteViewDetail,
    ProductViewSet,
)

router = DefaultRouter()
router.register("", ProductViewSet, basename="product")


urlpatterns = router.urls

# urlpatterns = [
#     path("", ProductListCreateView.as_view(), name="product-list"),
#     path(
#         "<int:pk>/", ProductGetUpdateDeleteViewDetail.as_view(), name="product-detail"
#     ),
#     # path("get", ProductList.as_view()),
#     # path("new/", ProductCreate.as_view()),
# ]
