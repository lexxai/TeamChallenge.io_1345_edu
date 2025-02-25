from django.urls import path

from users.api_views import (
    BasicAuthLoginView,
    SessionToTokenView,
    DemoUsersView,
    TaggedTokenObtainPairView,
    TaggedTokenRefreshView,
)
from users.serializers import CustomTokenObtainPairSerializer


urlpatterns = [
    # JWT Token endpoints
    path(
        "token/",
        TaggedTokenObtainPairView.as_view(
            serializer_class=CustomTokenObtainPairSerializer
        ),
        name="token_obtain_pair",
    ),
    path(
        "token/refresh/",
        TaggedTokenRefreshView.as_view(),
        name="token_refresh",
    ),
    path("login/", BasicAuthLoginView.as_view(), name="basic_auth_login"),
    path("session-to-token/", SessionToTokenView.as_view(), name="session_to_token"),
    path("users/demo/", DemoUsersView.as_view(), name="users_demo"),
]
