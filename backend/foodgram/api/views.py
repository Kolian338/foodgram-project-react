from django.db.models import Sum
from django.http import HttpResponse
from rest_framework.generics import get_object_or_404
from djoser.views import UserViewSet

from api.permissions import AuthenticatedUserOrReadOnly
from rest_framework.permissions import AllowAny, IsAuthenticatedOrReadOnly
from api.serializers import (
    CustomUserCreateSerializer, SubscribeSerializer,
    TagSerializer, RecipeIngredientReadSerializer,
    RecipeWriteSerializer,
    RecipeReadSerializer, IngredientSerializer,
    RecipeUserSerializer, FavoriteWriteSerializer, ShoppingCartWriteSerializer
)
from users.models import User, Subscription
from recipes.models import Tag, Ingredient, Recipe, Favorite, ShoppingCart, \
    RecipeIngredient
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
        if self.action == 'retrieve' or self.action == 'list':
            return (AuthenticatedUserOrReadOnly(),)
        return super().get_permissions()

    @action(
        methods=['post'], detail=True,
        permission_classes=[AuthenticatedUserOrReadOnly]
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
        permission_classes=[AuthenticatedUserOrReadOnly]
    )
    def subscriptions(self, request):
        subscribers = User.objects.filter(
            author__user_id=request.user.id
        )

        page = self.paginate_queryset(subscribers)
        if page is not None:
            serializer = RecipeUserSerializer(page, many=True,
                                              context={'request': request})
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(subscribers, many=True)
        return Response(serializer.data)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return RecipeReadSerializer
        return RecipeWriteSerializer

    @action(methods=['post'], detail=True)
    def favorite(self, request, pk=None):
        recipe = self.get_object()
        user = self.request.user
        serializer = FavoriteWriteSerializer(
            data={'user': user.id, 'recipe': recipe.id}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @favorite.mapping.delete
    def remove_from_favorite(self, request, pk=None):
        recipe = self.get_object()
        favorite = Favorite.objects.filter(
            recipe=recipe, user=self.request.user
        )

        if favorite:
            favorite.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['post'], detail=True)
    def shopping_cart(self, request, pk=None):
        recipe = self.get_object()
        user = self.request.user
        serializer = ShoppingCartWriteSerializer(
            data={'user': user.id, 'recipe': recipe.id}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @shopping_cart.mapping.delete
    def remove_from_shopping_cart(self, request, pk=None):
        recipe = self.get_object()
        shopping_cart = ShoppingCart.objects.filter(
            recipe=recipe, user=self.request.user
        )

        if shopping_cart:
            shopping_cart.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'])
    def download_shopping_cart(self, request):
        result = RecipeIngredient.objects.filter(
            recipe__shopping_cart__user=self.request.user
        ).values(
            'ingredient__name', 'ingredient__measurement_unit'
        ).annotate(
            total_amount=Sum('amount')
        ).order_by(
            'ingredient__name'
        )
        result_list = []
        for ingredient in result:
            name = ingredient['ingredient__name']
            total_amount = ingredient['total_amount']
            measurement_unit = ingredient['ingredient__measurement_unit']
            result_list.append(
                f"{name} - {total_amount} {measurement_unit} \n"
            )

        response = HttpResponse(result_list, content_type='text/plain')
        response['Content-Disposition'] = (
            f'attachment; filename="testfilename"'
        )
        return response

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
