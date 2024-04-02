from djoser.views import UserViewSet

from api.permissions import AuthenticatedUser
from rest_framework.permissions import AllowAny, IsAuthenticatedOrReadOnly
from api.serializers import CustomUserSerializer
from users.models import User
from rest_framework import viewsets


class CustomUserViewSet(UserViewSet):
    """
    Кастомный вьюсет наследованный от базового djoser.
    """
    serializer_class = CustomUserSerializer

    def get_queryset(self):
        return User.objects.all()

    def get_permissions(self):
        if self.action == 'retrieve':
            return (AuthenticatedUser(),)
        return super().get_permissions()
