from django.urls import path

from .api_views import ProductListCreateUpdateView, ProductListCreateUpdateViewDetail

urlpatterns = [
    path("", ProductListCreateUpdateView.as_view(), name="product-list"),
    path(
        "<int:pk>/", ProductListCreateUpdateViewDetail.as_view(), name="product-detail"
    ),
    # path("get", ProductList.as_view()),
    # path("new/", ProductCreate.as_view()),
]
