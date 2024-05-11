from django.contrib import admin

from recipes.models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                            ShoppingCart, Tag)


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ['pk', 'name', 'measurement_unit']
    search_fields = ['name']
    list_filter = ['name']
    empty_value_display = '-----'


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['pk', 'name', 'color', 'slug']
    search_fields = ['name', 'color', 'slug']
    list_filter = ['name', 'color', 'slug']
    empty_value_display = '-----'


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    min_num = 1


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ['pk', 'name', 'author', 'favorites']
    search_fields = ['name', 'author__username']
    list_filter = ['name', 'author', 'tags']
    empty_value_display = '-----'
    inlines = [
        RecipeIngredientInline,
    ]

    def favorites(self, obj):
        return obj.favorites.count()


@admin.register(RecipeIngredient)
class RecipeIngredientAdmin(admin.ModelAdmin):
    list_display = ['pk', 'recipe', 'ingredient', 'amount']
    empty_value_display = '-----'


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'recipe']
    search_fields = ['user__username', 'user__email']
    empty_value_display = '-----'


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'recipe']
    search_fields = ['user__username', 'user__email']
    empty_value_display = '-----'
