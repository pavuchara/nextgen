from django.contrib import admin
from .models import NextgenUser, UserProfile


@admin.register(NextgenUser)
class NextgenUserAdmin(admin.ModelAdmin):
    """Админ-панель пользователя."""
    pass


@admin.register(UserProfile)
class UserProfile(admin.ModelAdmin):
    """Админ-панель профиля пользователя."""

    list_display = ('user', 'slug')
