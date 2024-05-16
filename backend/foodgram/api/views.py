from django.db.models import Sum
from django.http import Http404, HttpResponse
from django_filters.rest_framework.backends import DjangoFilterBackend
from djoser.views import UserViewSet as BaseUserViewSet
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import (IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response

from api.filters import IngredientFilter, RecipeFilter
from api.paginators import PageLimitPagination
from api.permissions import Author
from api.serializers import (FavoriteWriteSerializer, IngredientSerializer,
                             RecipeReadSerializer, RecipeUserSerializer,
                             RecipeWriteSerializer,
                             ShoppingCartWriteSerializer, SubscribeSerializer,
                             TagSerializer)
from recipes import constants
from recipes.models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                            ShoppingCart, Tag)
from users.models import Subscription, User


class UserViewSet(BaseUserViewSet):
    pagination_class = LimitOffsetPagination

    def get_queryset(self):
        return User.objects.all()

    def get_permissions(self):
        if self.action == 'retrieve' or self.action == 'list':
            return (IsAuthenticatedOrReadOnly(),)
        return super().get_permissions()

    @action(
        methods=['post'], detail=True,
        permission_classes=[Author, IsAuthenticatedOrReadOnly]
    )
    def subscribe(self, request, id=None):
        author = get_object_or_404(
            User, pk=id
        )

        serializer = SubscribeSerializer(
            data={'author': author.id, 'user': request.user.id},
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @subscribe.mapping.delete
    def unsubscribe(self, request, id=None):
        author = get_object_or_404(User, id=id)
        try:
            subscription = get_object_or_404(
                Subscription, author_id=author, user_id=request.user.id
            )
        except Http404:
            return Response("Нет такой подписки!",
                            status=status.HTTP_400_BAD_REQUEST)

        subscription.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        methods=['get'], detail=False,
        permission_classes=[Author, IsAuthenticatedOrReadOnly]
    )
    def subscriptions(self, request):
        subscribers = User.objects.filter(
            subscribing__user_id=request.user.id
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
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = (Author, IsAuthenticatedOrReadOnly)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    pagination_class = PageLimitPagination
    #pagination_class = LimitOffsetPagination

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return RecipeReadSerializer
        return RecipeWriteSerializer

    @action(
        methods=['post'], detail=True,
        permission_classes=(IsAuthenticated,)
    )
    def favorite(self, request, pk=None):
        try:
            recipe = self.get_object()
        except Http404:
            return Response("Нет такого рецепта",
                            status=status.HTTP_400_BAD_REQUEST)
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

    @action(
        methods=['post'], detail=True,
        permission_classes=(IsAuthenticated,)
    )
    def shopping_cart(self, request, pk):
        try:
            recipe = self.get_object()
        except Http404:
            return Response("Нет такого рецепта",
                            status=status.HTTP_400_BAD_REQUEST)

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

    @action(
        detail=False, methods=['get'],
        permission_classes=(IsAuthenticated,)
    )
    def download_shopping_cart(self, request):
        result = RecipeIngredient.objects.filter(
            recipe__shopping_carts__user=self.request.user
        ).values(
            'ingredient__name', 'ingredient__measurement_unit'
        ).annotate(
            total_amount=Sum('amount')
        ).order_by(
            'ingredient__name'
        )

        data = self.parse_ingredients(result)
        return self.download_file(content=data, filename=constants.FILE_NAME)

    def parse_ingredients(self, result):
        parsed_result = []
        for ingredient in result:
            name = ingredient['ingredient__name']
            total_amount = ingredient['total_amount']
            measurement_unit = ingredient['ingredient__measurement_unit']
            parsed_result.append(
                f"{name} - {total_amount} {measurement_unit} \n"
            )
        return parsed_result

    def download_file(self, content, filename):
        response = HttpResponse(content, content_type='text/plain')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response
