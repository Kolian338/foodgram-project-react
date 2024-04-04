from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Кастомная модель юзера."""
    email = models.EmailField(
        'Адрес электронной почты', max_length=254
    )
    first_name = models.CharField('Имя', max_length=150)
    last_name = models.CharField('Фамилия', max_length=150)
    password = models.CharField('Пароль', max_length=150)

    def __str__(self):
        return self.username


class Follow(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='follower',
        verbose_name='Подписчик'
    )
    following = models.ForeignKey(
        User, on_delete=models.SET_NULL, related_name='following',
        blank=True, null=True,
        verbose_name='Подписка'
    )

    class Meta:
        """
        - Проверка составной уникальности в UniqueConstraint
        - Ограничение подписки на самого себя в CheckConstraint
        """

        constraints = [
            models.UniqueConstraint(
                fields=['user', 'following'],
                name='unique_user_following'
            ),
            models.CheckConstraint(
                name='cant_subscribe_to_yourself',
                check=~models.Q(user=models.F('following')),
            ),
        ]

    def __str__(self):
        return f'{self.user} {self.following}'