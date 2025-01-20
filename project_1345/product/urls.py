from django.urls import path

from .api_views import ProductList, ProductCreate, ProductListCreateUpdateView

urlpatterns = [
    path("", ProductListCreateUpdateView.as_view(), name="product-list-create"),
    path("<int:pk>/", ProductListCreateUpdateView.as_view(), name="product-detail"),
    path("get", ProductList.as_view()),
    path("new/", ProductCreate.as_view()),
]
