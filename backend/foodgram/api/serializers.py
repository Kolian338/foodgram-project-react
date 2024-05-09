from djoser.serializers import (
    UserCreateSerializer as UserCreateSerializerDjoser)
from rest_framework import serializers

from drf_extra_fields.fields import Base64ImageField
from recipes.models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                            RecipeTag, ShoppingCart, Tag)
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
        fields = (
            'email', 'id', 'username', 'password', 'first_name', 'last_name',
            'is_subscribed', 'recipes', 'recipes_count',
        )

    def get_recipes(self, obj):
        request = self.context.get('request')
        recipes_limit = None

        if request:
            recipes_limit = request.query_params.get('recipes_limit')
        recipes = obj.recipes.all()

        if recipes_limit:
            recipes = recipes[:int(recipes_limit)]

        serializer = RecipeSerializer(recipes, many=True, context=self.context)
        return serializer.data

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
    ingredients = RecipeIngredientWriteSerializer(
        many=True, allow_empty=False,
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

    def validate_ingredients(self, ingredients):
        if not ingredients:
            raise serializers.ValidationError(
                'Нет ингридиентов!'
            )

        ingredient_list = []
        for ingredient in ingredients:
            ingredient_list.append(ingredient.get('ingredient'))

        if len(set(ingredient_list)) != len(ingredient_list):
            raise serializers.ValidationError(
                'Ингредиенты должны быть уникальными!'
            )
        return ingredients

    def validate_tags(self, tags):
        if not tags:
            raise serializers.ValidationError(
                'Тэги не могут быть пустыми!'
            )

        tag_ids = [tag.id for tag in tags]
        if len(set(tag_ids)) != len(tag_ids):
            raise serializers.ValidationError('Теги должны быть уникальными!')
        return tags

    def create(self, validated_data):
        author = self.context.get('request').user
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')

        recipe = Recipe.objects.create(**validated_data, author=author)

        for tag in tags:
            RecipeTag.objects.create(recipe=recipe, tag=tag)
        for ingredient in ingredients:
            RecipeIngredient.objects.create(
                ingredient=ingredient.get('ingredient'),
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
        self.validate_ingredients(ingredients_valid)

        tags_valid = validated_data.pop('tags', None)
        self.validate_tags(tags_valid)
        if tags_valid is not None:
            instance.tags.set(tags_valid)

        if ingredients_valid is not None:
            instance.ingredients.clear()

            for ingredient in ingredients_valid:
                RecipeIngredient.objects.create(
                    recipe=instance,
                    ingredient=ingredient.get('ingredient'),
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
