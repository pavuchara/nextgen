from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth import get_user_model

from .models import UserProfile

# Получение модели пользователя.
NextgenUser = get_user_model()

# Регистрация переопределенной модели пользователя
admin.site.register(NextgenUser, UserAdmin)


@admin.register(UserProfile)
class UserProfile(admin.ModelAdmin):
    """Админ-панель профиля пользователя."""

    list_display = ('user', 'slug')
