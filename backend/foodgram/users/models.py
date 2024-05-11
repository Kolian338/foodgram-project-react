from django.contrib.auth import validators
from django.contrib.auth.models import AbstractUser
from django.db import models
from users import constants
from users.validators import validate_username


class User(AbstractUser):
    """Кастомная модель юзера."""

    email = models.EmailField(
        'Адрес электронной почты', max_length=constants.MAX_EMAIL_LENGTH,
        unique=True
    )
    first_name = models.CharField(
        'Имя', max_length=constants.MAX_FIRST_NAME_LENGTH
    )
    last_name = models.CharField(
        'Фамилия', max_length=constants.MAX_LAST_NAME_LENGTH
    )
    password = models.CharField(
        'Пароль', max_length=constants.MAX_PASSWORD_LENGTH
    )
    username = models.CharField(
        'Юзернейм', max_length=constants.MAX_USERNAME_LENGTH,
        validators=[validate_username, validators.UnicodeUsernameValidator]
    )
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ('first_name', 'last_name', 'username',)

    def __str__(self):
        return self.username


class Subscription(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='subscriber',
        verbose_name='Подписчик'
    )
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='subscribing',
        verbose_name='Автор'
    )

    class Meta:
        """
        - Проверка составной уникальности в UniqueConstraint
        - Ограничение подписки на самого себя в CheckConstraint
        """

        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'],
                name='unique_user_author'
            ),
            models.CheckConstraint(
                name='cant_subscribe_to_yourself',
                check=~models.Q(user=models.F('author')),
            ),
        ]
        verbose_name = 'Подписчик'
        verbose_name_plural = 'Подписчики'

    def __str__(self):
        return f'{self.user} {self.author}'
