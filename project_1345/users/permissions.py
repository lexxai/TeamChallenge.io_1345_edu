from rest_framework.permissions import BasePermission


class IsInGroup(BasePermission):
    """
    Custom permission to grant access to users in specific groups.
    """

    required_groups = ["managers"]  # Set the required groups here

    def has_permission(self, request, view):
        # Check if the user is authenticated
        if not request.user or not request.user.is_authenticated:
            return False

        # Check if the user belongs to any of the required groups
        user_groups = request.user.groups.values_list("name", flat=True)
        return any(group in self.required_groups for group in user_groups)


class IsAuthenticatedOrReadOnly(BasePermission):
    """
    Custom permission to allow read-only access for unauthenticated users
    and restrict write access to authenticated users with specific roles (e.g., managers).
    """

    managers_groups = ["managers"]  # Set the required groups here

    def has_permission(self, request, view):
        # Allow read-only methods (GET, HEAD, OPTIONS) for everyone
        if request.method in ["GET", "HEAD", "OPTIONS"]:
            return True

        # For write methods, check if the user is authenticated and has the required role
        if request.user and request.user.is_authenticated:
            return (
                request.user.is_staff  # Allow staff
                or request.user.groups.filter(
                    name__in=self.managers_groups
                ).exists()  # Allow managers
            )

        # Deny access for unauthenticated users
        return False


class IsInJWTGroup(BasePermission):
    """
    Custom permission to check groups directly from the JWT token.
    """

    required_groups = ["managers"]

    def has_permission(self, request, view):
        # Check if the user is authenticated and the JWT has 'groups' claim
        if not request.user or not request.auth or "groups" not in request.auth:
            return False

        # Check if any required group is in the JWT's 'groups' claim
        user_groups = request.auth["groups"]
        return any(group in self.required_groups for group in user_groups)
