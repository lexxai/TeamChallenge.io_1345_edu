from django.urls import path

from .api_views import ProductListCreateView, ProductGetUpdateDeleteViewDetail

urlpatterns = [
    path("", ProductListCreateView.as_view(), name="product-list"),
    path(
        "<int:pk>/", ProductGetUpdateDeleteViewDetail.as_view(), name="product-detail"
    ),
    # path("get", ProductList.as_view()),
    # path("new/", ProductCreate.as_view()),
]
