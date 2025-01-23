from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from users.api_views import BasicAuthLoginView, SessionToTokenView
from users.serializers import CustomTokenObtainPairSerializer


urlpatterns = [
    # JWT Token endpoints
    path(
        "token/",
        TokenObtainPairView.as_view(serializer_class=CustomTokenObtainPairSerializer),
        name="token_obtain_pair",
    ),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("login/", BasicAuthLoginView.as_view(), name="basic_auth_login"),
    path("session-to-token/", SessionToTokenView.as_view(), name="session_to_token"),
]
