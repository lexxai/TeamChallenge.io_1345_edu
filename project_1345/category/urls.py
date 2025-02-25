from django.urls import path

from .api_views import CategorySchemaList, CategoryList

urlpatterns = [
    path("", CategoryList.as_view()),
    path("schema/", CategorySchemaList.as_view()),
]
