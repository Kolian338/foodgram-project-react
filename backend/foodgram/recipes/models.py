from colorfield.fields import ColorField
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import UniqueConstraint

from recipes import constants
from users.models import User


class Tag(models.Model):
    name = models.CharField(
        'Название', max_length=constants.MAX_NAME_LENGTH, unique=True
    )
    color = ColorField(
        'Цвет в HEX', max_length=constants.MAX_COLOR_LENGTH, unique=True
    )
    slug = models.SlugField(max_length=constants.MAX_SLUG_LENGTH, unique=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField('Название', max_length=constants.MAX_NAME_LENGTH)
    measurement_unit = models.CharField(
        'Единицы измерения', max_length=constants.MAX_MEASUREMENT_UNIT_LENGTH
    )

    class Meta:
        ordering = ['name']
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        constraints = [
            UniqueConstraint(
                fields=['name', 'measurement_unit'],
                name='unique_name_measurement_unit'
            )
        ]

    def __str__(self):
        return f'{self.name} {self.measurement_unit}'


class Recipe(models.Model):
    author = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='recipes'
    )
    name = models.CharField('Название', max_length=constants.MAX_NAME_LENGTH)
    image = models.ImageField('Изображение', upload_to='recipes/images')
    text = models.TextField('Описание')
    ingredients = models.ManyToManyField(
        Ingredient, through='RecipeIngredient',
        related_name='recipes',
    )
    tags = models.ManyToManyField(
        Tag, through='RecipeTag',
        related_name='recipes',
    )
    cooking_time = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(
            constants.COOKING_TIME,
            f'Время готовки не может быть меньше {constants.COOKING_TIME} мин.'
        )
        ],
        verbose_name='Время готовки'
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True
    )

    class Meta:
        ordering = ['-pub_date']
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return f'{self.name} {self.text}'


class RecipeTag(models.Model):
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE,
        related_name='recipes_tags'
    )
    tag = models.ForeignKey(
        Tag, on_delete=models.CASCADE,
        related_name='recipes_tags'
    )

    class Meta:
        ordering = ['tag']
        constraints = [
            UniqueConstraint(
                fields=['recipe', 'tag'],
                name='unique_recipe_tag'
            )
        ]

    def __str__(self):
        return f'{self.recipe} {self.tag}'


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE,
        related_name='recipes_ingredients',
        verbose_name='Рецепт'
    )
    ingredient = models.ForeignKey(
        Ingredient, on_delete=models.CASCADE,
        related_name='recipes_ingredients',
        verbose_name='Ингредиент'
    )
    amount = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(
            constants.COOKING_TIME, (
                f'Количество ингредиентов не может быть меньше'
                f'{constants.COOKING_TIME}'
            )
        ), ]
    )

    class Meta:
        ordering = ['recipe']
        verbose_name = 'Рецепт с ингредиентом'
        verbose_name_plural = 'Рецепты с игридиентами'
        constraints = [
            UniqueConstraint(
                fields=['recipe', 'ingredient'],
                name='unique_recipe_ingredient'
            )
        ]

    def __str__(self):
        return f"{self.recipe} {self.ingredient} - {self.amount}"


class Favorite(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='favorites'
    )
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE,
        related_name='favorites'
    )

    class Meta:
        ordering = ['recipe']
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_user_recipe'
            )
        ]

    def __str__(self):
        return f'Рецепт {self.recipe} в избранном у {self.user}'


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='shopping_carts'
    )
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE,
        related_name='shopping_carts'
    )

    class Meta:
        ordering = ['recipe']
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_user_recipe_shoppingcart'
            )
        ]

    def __str__(self):
        return f"{self.recipe} {self.user}"
