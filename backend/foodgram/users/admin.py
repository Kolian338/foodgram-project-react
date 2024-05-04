from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib import admin
from users.models import User, Subscription


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = (
        "is_active", "username", "first_name", "last_name", "email",
    )
    list_editable = ("username", "email", "password",)
    search_fields = ("username", "email",)
    list_filter = ("is_active", "first_name", "email",)


@admin.register(Subscription)
class SubscribeAdmin(admin.ModelAdmin):
    list_display = ('user', 'author',)
