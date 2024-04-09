from djoser.serializers import UserSerializer, UserCreateSerializer
from users.models import User, Subscription
from rest_framework import serializers


class IsSubscribedMixin(metaclass=serializers.SerializerMetaclass):
    """
    """
    is_subscribed = serializers.SerializerMethodField()

    def get_is_subscribed(self, obj):
        """
        Подписан ли текущий пользователь на переданного.
        obj - переданный юзер в url
        current_user - юзер из запроса
        """
        current_user = self.context.get('request').user
        return (current_user.is_authenticated
                and Subscription.objects.filter(
                    author__id=obj.id, user_id=current_user.id
                ).exists())


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
    ...


class SubscribeWriteSerializer(IsSubscribedMixin, serializers.ModelSerializer):
    recipes = ...

    class Meta:
        model = Subscription
        fields = ('author', 'user', 'is_subscribed',)
        extra_kwargs = {
            'author': {'write_only': True},
            'user': {'write_only': True},
        }

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
