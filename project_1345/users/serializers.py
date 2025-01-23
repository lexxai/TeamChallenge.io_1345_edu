from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import serializers


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(
        max_length=150
    )  # Matches Django's default User model
    password = serializers.CharField(write_only=True, style={"input_type": "password"})


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def get_token(self, user):
        # Get the default token
        token = super().get_token(user)

        # Add custom claims (user groups)
        token["username"] = user.username
        token["is_staff"] = user.is_staff
        token["groups"] = [group.name for group in user.groups.all()]

        return token
