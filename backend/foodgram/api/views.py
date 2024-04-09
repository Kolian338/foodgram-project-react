from rest_framework.generics import get_object_or_404
from djoser.views import UserViewSet

from api.permissions import AuthenticatedUser
from rest_framework.permissions import AllowAny, IsAuthenticatedOrReadOnly
from api.serializers import CustomUserCreateSerializer, SubscribeWriteSerializer
from users.models import User
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response


class CustomUserViewSet(UserViewSet):
    """
    Кастомный вьюсет наследованный от базового djoser.
    Сериализатор берется из settings.
    """

    def get_queryset(self):
        return User.objects.all()

    def get_permissions(self):
        if self.action == 'retrieve':
            return (AuthenticatedUser(),)
        return super().get_permissions()

    @action(
        methods=['post', 'delete'], detail=True,
    )
    def subscribe(self, request, id=None):
        """
        - Подписка на юзера.
        - Удаление подписки.
        """
        if request.method == 'POST':
            author = get_object_or_404(
                User, pk=id
            )
            serializer = SubscribeWriteSerializer(
                data={'author': author.id, 'user': request.user.id},
                context={'request': request}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)

    @action(
        methods=['get'], detail=False,
    )
    def subscriptions(self):
        ...
