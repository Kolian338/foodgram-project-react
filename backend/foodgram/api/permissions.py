from rest_framework.permissions import (BasePermission, SAFE_METHODS)


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
        return (
                request.method in SAFE_METHODS
                or obj.author == request.user
        )
