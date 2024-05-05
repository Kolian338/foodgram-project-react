from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib import admin
from users.models import User, Subscription


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = (
        "is_active", "username", "first_name", "last_name", "email",
        "password", "recipe_count", "subscriber_count"
    )
    list_editable = ("username", "email", "password",)
    search_fields = ("username", "email",)
    list_filter = ("is_active", "first_name", "email",)

    def recipe_count(self, obj):
        return obj.recipes.count()

    recipe_count.short_description = 'Количество рецептов'

    def subscriber_count(self, obj):
        return obj.subscriber.count()

    subscriber_count.short_description = 'Количество подписчиков'


@admin.register(Subscription)
class SubscribeAdmin(admin.ModelAdmin):
    list_display = ('user', 'author',)
