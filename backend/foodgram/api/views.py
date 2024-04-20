from rest_framework.generics import get_object_or_404
from djoser.views import UserViewSet

from api.permissions import AuthenticatedUser
from rest_framework.permissions import AllowAny, IsAuthenticatedOrReadOnly
from api.serializers import CustomUserCreateSerializer, SubscribeSerializer, \
    TagSerializer, IngredientReadSerializer, RecipeWriteSerializer, RecipeReadSerializer
from users.models import User, Subscription
from recipes.models import Tag, Ingredient, Recipe
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status


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
        methods=['post'], detail=True,
    )
    def subscribe(self, request, id=None):
        """
        - Подписка на юзера.
        - Удаление подписки.
        """
        author = get_object_or_404(
            User, pk=id
        )

        serializer = SubscribeSerializer(
            data={'author': author.id, 'user': request.user.id},
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @subscribe.mapping.delete
    def unsubscribe(self, request, id=None):
        subscription = get_object_or_404(
            Subscription, author_id=id, user_id=request.user.id
        )
        subscription.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        methods=['get'], detail=False,
    )
    def subscriptions(self, request):
        subscribers = User.objects.filter(
            author__user_id=request.user.id
        )

        page = self.paginate_queryset(subscribers)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(subscribers, many=True)
        return Response(serializer.data)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientReadSerializer
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return RecipeReadSerializer
        return RecipeWriteSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
