from djoser.serializers import UserSerializer, UserCreateSerializer
from users.models import User
from rest_framework import serializers


class CustomUserSerializer(UserCreateSerializer):
    """
    Кастомный сериализатор от модели.
    """

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'password', 'first_name', 'last_name',
            # 'is_subscribed',
        )
        read_only_fields = ('id',)
        extra_kwargs = {'password': {'write_only': True}}
