from django.core.validators import MinValueValidator
from django.db import models
from users.models import User


class Tag(models.Model):
    name = models.CharField('Название', max_length=200, unique=True)
    color = models.CharField('Цвет в HEX', max_length=6, unique=True)
    slug = models.SlugField(max_length=200, unique=True)

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField('Название', max_length=200)
    measurement_unit = models.CharField('Единицы измерения', max_length=200)

    def __str__(self):
        return f'{self.name} {self.measurement_unit}'


class Recipe(models.Model):
    author = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='recipes'
    )
    name = models.CharField('Название', max_length=200)
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
            1, 'Время готовки не может быть меньше 1 мин.'
        )
        ],
        verbose_name='Время готовки'
    )


class RecipeTag(models.Model):
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE,
        related_name='recipes_tags'
    )
    tag = models.ForeignKey(
        Tag, on_delete=models.CASCADE,
        related_name='recipes_tags'
    )

    def __str__(self):
        return f'{self.recipe} {self.tag}'


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE,
        related_name='recipes_ingredients'
    )
    ingredient = models.ForeignKey(
        Ingredient, on_delete=models.CASCADE,
        related_name='recipes_ingredients'
    )
    amount = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(
            1, 'Количество ингредиентов не может быть меньше 1'
        ),
        ]
    )


class Favorite(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='favorites'
    )
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE,
        related_name='recipes'
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_user_recipe'
            )
        ]
