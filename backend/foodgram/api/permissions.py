from rest_framework import permissions
from rest_framework.permissions import BasePermission


class Author(BasePermission):
    """
    Пользовательский класс разрешений.
    """

    def has_object_permission(self, request, view, obj):
        """
        Возвращает `True` если есть рашрешение иначе `False`.

        Параметры:
        request - запрос
        view - представление
        obj - объект к которому нужен доступ
        """

        return (request.method in permissions.SAFE_METHODS
                or obj.author == request.user)
