from django.urls import path

from .api_views import ProductList, ProductCreate, ProductListCreateView

urlpatterns = [
    path("", ProductListCreateView.as_view()),
    path("get", ProductList.as_view()),
    path("new/", ProductCreate.as_view()),
]
