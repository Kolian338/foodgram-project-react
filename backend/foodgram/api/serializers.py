from djoser.serializers import UserSerializer, UserCreateSerializer
from users.models import User
from rest_framework import serializers


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


class CustomUserSerializer(CustomUserCreateSerializer):
    """
    Сериализатор для:
    - GET /api/users/
    - GET /api/users/1/
    - GET /api/users/me/
    """
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'password', 'first_name', 'last_name',
            'is_subscribed',
        )
        read_only_fields = ('id',)

    def get_is_subscribed(self, obj):
        # написать логику
        return True
