from djoser.serializers import \
    UserCreateSerializer as UserCreateSerializerDjoser
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from recipes import constants
from recipes.models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                            ShoppingCart, Tag)
from users.models import Subscription, User


class IsSubscribedMixin(metaclass=serializers.SerializerMetaclass):
    is_subscribed = serializers.SerializerMethodField()

    def get_is_subscribed(self, obj):
        """
        Подписан ли текущий пользователь на переданного.
        obj - объект автора.
        """
        current_user = self.context.get('request').user
        return (current_user.is_authenticated
                and obj.subscribing.filter(user=current_user).exists())


class UserCreateSerializer(UserCreateSerializerDjoser):
    """Сериализатор записи/чтения с моделью User."""

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'password', 'first_name', 'last_name',
        )


class UserSerializer(IsSubscribedMixin, UserCreateSerializer):
    """Сериализатор чтения с моделью User."""

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'password', 'first_name', 'last_name',
            'is_subscribed',
        )


class RecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = (
            'id', 'name', 'image', 'cooking_time',
        )


class RecipeUserSerializer(UserSerializer, serializers.ModelSerializer):
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = UserSerializer.Meta.fields + ('recipes', 'recipes_count')

    def get_recipes(self, obj):
        request = self.context.get('request')
        recipes_limit = None

        if request:
            recipes_limit_param = request.query_params.get('recipes_limit')
            if recipes_limit_param:
                try:
                    recipes_limit = int(recipes_limit_param)
                except ValueError:
                    raise serializers.ValidationError(
                        'Не целое число', code='error'
                    )
        recipes = obj.recipes.all()

        if recipes_limit:
            recipes = recipes[:int(recipes_limit)]

        serializer = RecipeSerializer(recipes, many=True, context=self.context)
        return serializer.data

    def get_recipes_count(self, obj):
        return obj.recipes.count()


class SubscribeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        fields = ('author', 'user',)
        extra_kwargs = {
            'author': {'write_only': True},
            'user': {'write_only': True},
        }

    def validate(self, attrs):
        if Subscription.objects.filter(
                author=attrs['author'], user=attrs['user']
        ):
            raise serializers.ValidationError('Уже есть подписка',
                                              code='error')

        if self.context['request'].method == 'POST':
            if attrs['author'] == attrs['user']:
                raise serializers.ValidationError('Подписка на самого себя',
                                                  code='error')
        return attrs

    def to_representation(self, instance):
        return RecipeUserSerializer(instance.author, context=self.context).data


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
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(), source='ingredient'
    )
    amount = serializers.IntegerField(
        max_value=constants.MAX_INGREDIENT_AMOUNT,
        min_value=constants.MIN_INGREDIENT_AMOUNT
    )

    class Meta:
        model = RecipeIngredient
        fields = (
            'id', 'amount'
        )


class RecipeReadSerializer(serializers.ModelSerializer):
    """
    Сериализатор для чтения /api/recipes/
    ingredients - передаются записи из таблицы RecipeIngredient от ингридиента.
    """
    tags = TagSerializer(many=True)
    author = UserSerializer()
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
        return (request is not None
                and request.user.is_authenticated
                and request.user.favorites.filter(recipe=obj).exists()
                )

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        return (request is not None
                and request.user.is_authenticated
                and request.user.shopping_carts.filter(recipe=obj).exists()
                )


class RecipeWriteSerializer(serializers.ModelSerializer):
    ingredients = RecipeIngredientWriteSerializer(
        many=True
    )
    tags = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Tag.objects.all()
    )
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'ingredients', 'tags', 'image', 'name', 'text', 'cooking_time'
        )

    def validate(self, data):
        if not data.get('image'):
            raise serializers.ValidationError(
                {
                    'image': 'Пустая картинка!'
                }
            )

        tags_data = data.get('tags')
        if not tags_data:
            raise serializers.ValidationError(
                'Тэги не могут быть пустыми!'
            )

        if len(set(tags_data)) != len(tags_data):
            raise serializers.ValidationError('Теги должны быть уникальными!')

        ingredients_data = data.get('ingredients')
        if not ingredients_data:
            raise serializers.ValidationError(
                {
                    'ingredients': 'Нужен хотя бы один ингредиент!'
                }
            )

        ingredient_list = []
        for ingredient in ingredients_data:
            ingredient_list.append(ingredient.get('ingredient'))

        ingredient_ids = (
            ingredient.get('ingredient') for ingredient in ingredients_data
        )
        if len(set(ingredient_ids)) != len(ingredients_data):
            raise serializers.ValidationError(
                'Ингредиенты должны быть уникальными!'
            )
        return data

    def create(self, validated_data):
        author = self.context.get('request').user
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')

        recipe = Recipe.objects.create(**validated_data, author=author)
        recipe.tags.set(tags)

        recipe_ingredients = [
            RecipeIngredient(
                ingredient=ingredient.get('ingredient'),
                amount=ingredient.get('amount'),
                recipe=recipe
            )
            for ingredient in ingredients
        ]
        RecipeIngredient.objects.bulk_create(recipe_ingredients)

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
        instance.ingredients.clear()

        for ingredient in ingredients_valid:
            RecipeIngredient.objects.create(
                recipe=instance,
                ingredient=ingredient.get('ingredient'),
                amount=ingredient.get('amount'),
            )

        return super().update(instance, validated_data)

    def to_representation(self, instance):
        return RecipeReadSerializer(instance, context=self.context).data


class FavoriteWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Favorite
        fields = (
            'user', 'recipe',
        )
        validators = [
            UniqueTogetherValidator(
                queryset=Favorite.objects.all(),
                fields=('user', 'recipe')
            )
        ]

    def to_representation(self, instance):
        return RecipeSerializer(instance.recipe).data


class ShoppingCartWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShoppingCart
        fields = (
            'user', 'recipe',
        )
        validators = [
            UniqueTogetherValidator(
                queryset=ShoppingCart.objects.all(),
                fields=('user', 'recipe')
            )
        ]

    def to_representation(self, instance):
        return RecipeSerializer(instance.recipe).data
