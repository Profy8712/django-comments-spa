from rest_framework.permissions import BasePermission


class IsStaffOrSuperuser(BasePermission):
    """
    Allow only authenticated staff/superuser users.
    """
    def has_permission(self, request, view):
        user = getattr(request, "user", None)
        return bool(
            user
            and user.is_authenticated
            and (user.is_staff or user.is_superuser)
        )
