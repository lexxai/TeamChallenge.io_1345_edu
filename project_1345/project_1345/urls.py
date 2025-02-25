import sys
import re

from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView
from django.views.static import serve

from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)

urlpatterns = [
    path("", RedirectView.as_view(url="/docs/swagger/", permanent=False)),
    # path(
    #     "",
    #     SpectacularSwaggerView.as_view(url_name="schema"),
    #     name="swagger-root",
    # ),
    path("schema/", SpectacularAPIView.as_view(), name="schema"),
    # Swagger UI
    path(
        "docs/swagger/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    # ReDoc UI
    path("docs/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
    path("admin/", admin.site.urls),
    path("api/v1/cart/", include("cart.urls")),
    path("api/v1/products/", include("product.urls")),
    path("api/v1/category/", include("category.urls")),
    path("api/v1/", include("users.urls")),
    path("api-auth/", include("rest_framework.urls", namespace="rest_framework")),
]

if "--insecure" in sys.argv:
    print("** Including static files media --insecure")

    def custom_static(prefix, view=serve, **kwargs):
        return [
            re_path(
                r"^%s(?P<path>.*)$" % re.escape(prefix.lstrip("/")),
                view,
                kwargs=kwargs,
            ),
        ]

    urlpatterns += custom_static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
elif settings.DEBUG:
    print("** Including static files media in DEBUG")
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
