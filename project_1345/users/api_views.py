from typing import List

from django.core.cache import cache
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema_view, extend_schema
from rest_framework.generics import GenericAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, serializers
from rest_framework.authentication import BasicAuthentication
from rest_framework.permissions import (
    AllowAny,
    IsAuthenticated,
    IsAuthenticatedOrReadOnly,
)
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from users.serializers import LoginSerializer


@extend_schema(tags=["Users"])
class BasicAuthLoginView(APIView):
    """
    Basic authentication login view.
    """

    authentication_classes = [BasicAuthentication]  # Use Basic Auth for login
    permission_classes = [AllowAny]  # Allow anyone to log in
    serializer_class = LoginSerializer

    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")

        # Authenticate the user
        user = authenticate(request, username=username, password=password)
        if user is not None:
            # Generate JWT tokens
            refresh = RefreshToken.for_user(user)
            return Response(
                {
                    "refresh": str(refresh),
                    "access": str(refresh.access_token),
                }
            )
        else:
            return Response(
                {"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED
            )


@extend_schema(tags=["Users"])
class SessionToTokenView(APIView):
    """
    Convert a logged-in session user into a JWT token.
    """

    serializer_class = None
    permission_classes = [IsAuthenticated]  # Ensure the user is logged in

    def get(self, request):
        user = request.user

        # Generate JWT tokens for the authenticated user
        refresh = RefreshToken.for_user(user)

        return Response(
            {
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            }
        )


class UserSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()


@extend_schema(tags=["Users"])
class DemoUsersView(APIView):
    """
    Retrieve a list of demo users. It temporarily stores them in the cache. Build on start up.
    """

    serializer_class = UserSerializer
    permission_classes = ()
    authentication_classes = ()

    @extend_schema(
        tags=["Users"],
        responses={
            200: UserSerializer(many=True),
            404: {"users": "No users found"},
        },
    )
    def get(self, request):
        cached_users: list | None = cache.get("demo_users")
        if cached_users:
            return Response(cached_users)
        return Response({"users": "No users found"}, status=status.HTTP_404_NOT_FOUND)


@extend_schema(tags=["Users"])
class TaggedTokenObtainPairView(TokenObtainPairView): ...


@extend_schema(tags=["Users"])
class TaggedTokenRefreshView(TokenRefreshView): ...
