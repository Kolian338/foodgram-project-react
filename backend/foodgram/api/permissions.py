from rest_framework import permissions
from rest_framework.permissions import SAFE_METHODS, BasePermission


class AuthenticatedUserOrReadOnly(BasePermission):
    """
    Читать могут все.
    Авторизованный юзер может редактировать/удалять только своё.
    """

    def has_permission(self, request, view):
        return bool(
            request.method in SAFE_METHODS
            or request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        return (request.method in permissions.SAFE_METHODS
                or request.user.is_superuser
                or request.user.is_staff
                or obj.author == request.user)
