import base64
from django.core.files.base import ContentFile

from djoser.serializers import UserSerializer, UserCreateSerializer
from rest_framework.validators import UniqueTogetherValidator
from rest_framework import request

from users.models import User, Subscription
from recipes.models import (
    Tag, Ingredient, Recipe, RecipeIngredient, RecipeTag, Favorite,
    ShoppingCart
)
from rest_framework import serializers


class IsSubscribedMixin(metaclass=serializers.SerializerMetaclass):
    """
    """
    is_subscribed = serializers.SerializerMethodField()

    def get_is_subscribed(self, obj):
        """
        Подписан ли текущий пользователь на переданного.
        obj - объект автора.
        """
        current_user = self.context.get('request').user
        return (current_user.is_authenticated
                and Subscription.objects.filter(
                    author__id=obj.id, user_id=current_user.id
                ).exists())


class Base64ImageField(serializers.ImageField):
    """
    Кастомное поле для декодирования картинки.
    """

    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]

            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


class CustomUserCreateSerializer(UserCreateSerializer):
    """
    Кастомный сериализатор от модели.
    - POST /api/users/
    -
    """

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'password', 'first_name', 'last_name',
        )
        read_only_fields = ('id',)


class CustomUserSerializer(IsSubscribedMixin, CustomUserCreateSerializer):
    """
    Сериализатор для:
    - GET /api/users/
    - GET /api/users/1/
    - GET /api/users/me/
    """

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'password', 'first_name', 'last_name',
            'is_subscribed',
        )
        read_only_fields = ('id',)


class RecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = (
            'id', 'name', 'image', 'cooking_time',
        )
        read_only_fields = ('id', 'name', 'image', 'cooking_time',)


class RecipeUserSerializer(CustomUserSerializer, serializers.ModelSerializer):
    recipes = RecipeSerializer(many=True)
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'password', 'first_name', 'last_name',
            'is_subscribed', 'recipes', 'recipes_count',
        )

    def get_recipes_count(self, obj):
        test = len(obj.recipes.all())
        return test


class SubscribeSerializer(IsSubscribedMixin, serializers.ModelSerializer):
    class Meta:
        model = Subscription
        fields = ('author', 'user', 'is_subscribed',)
        extra_kwargs = {
            'author': {'write_only': True},
            'user': {'write_only': True},
        }

    def validate(self, attrs):
        if self.context['request'].method == 'POST':
            if attrs['author'] == attrs['user']:
                raise serializers.ValidationError('Подписка на самого себя',
                                                  code='error')
        return attrs

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        request = self.context.get('request')
        if request:
            user = request.user
            representation = {
                'email': user.email,
                'id': user.id,
                'username': user.username,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "is_subscribed": self.get_is_subscribed(instance.author)
            }
        return representation


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = (
            'id', 'name', 'color', 'slug'
        )


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = (
            'id', 'name', 'measurement_unit',
        )


class RecipeIngredientReadSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = RecipeIngredient
        fields = (
            'id', 'name', 'measurement_unit', 'amount',
        )


class RecipeIngredientWriteSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    amount = serializers.IntegerField()

    class Meta:
        model = Ingredient
        fields = (
            'id', 'amount'
        )


class RecipeReadSerializer(serializers.ModelSerializer):
    """
    Сериализатор для чтения /api/recipes/
    ingredients - передаются записи из таблицы RecipeIngredient от ингридиента.
    """
    tags = TagSerializer(many=True)
    author = CustomUserSerializer()
    ingredients = RecipeIngredientReadSerializer(
        many=True, source='recipes_ingredients'
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients', 'is_favorited',
            'is_in_shopping_cart', 'name', 'image', 'text', 'cooking_time',
        )

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False

        return obj.favorites.filter(
            user=request.user
        ).exists()

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False

        return ShoppingCart.objects.filter(
            user=request.user
        ).exists()


class RecipeWriteSerializer(serializers.ModelSerializer):
    ingredients = RecipeIngredientWriteSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Tag.objects.all()
    )
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'ingredients', 'tags', 'image', 'name', 'text', 'cooking_time'
        )

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')

        recipe = Recipe.objects.create(**validated_data)

        for tag in tags:
            RecipeTag.objects.create(recipe=recipe, tag=tag)
        for ingredient in ingredients:
            RecipeIngredient.objects.create(
                ingredient=ingredient.get('id'),
                amount=ingredient.get('amount'),
                recipe=recipe
            )

        return recipe

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.image = validated_data.get('image', instance.image)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get(
            'cooking_time', instance.cooking_time
        )
        ingredients_valid = validated_data.pop('ingredients', None)
        tags_valid = validated_data.pop('tags', None)
        instance.tags.set(tags_valid)

        if ingredients_valid is not None:
            instance.ingredients.clear()

        for ingredient in ingredients_valid:
            RecipeIngredient.objects.create(
                recipe=instance,
                ingredient=ingredient.get('id'),
                amount=ingredient.get('amount'),
            )
        instance.save()

        return instance

    def to_representation(self, instance):
        return RecipeReadSerializer(instance, context=self.context).data


class FavoriteWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Favorite
        fields = (
            'user', 'recipe',
        )

    def to_representation(self, instance):
        return RecipeSerializer(instance.recipe).data


class ShoppingCartWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShoppingCart
        fields = (
            'user', 'recipe',
        )

    def to_representation(self, instance):
        return RecipeSerializer(instance.recipe).data
