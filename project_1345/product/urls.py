from django.urls import path

from .api_views import ProductList, ProductCreate

urlpatterns = [
    path("", ProductList.as_view()),
    path("new/", ProductCreate.as_view()),
]
