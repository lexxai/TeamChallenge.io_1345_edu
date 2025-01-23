from rest_framework.generics import GenericAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authentication import BasicAuthentication
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken

from users.serializers import LoginSerializer


class BasicAuthLoginView(APIView):
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
