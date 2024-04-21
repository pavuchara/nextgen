from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.core.cache import cache
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.core.validators import FileExtensionValidator

import os
from apps.services import constants
from apps.services.utils import unique_slugify, file_directory_path


class NextgenUser(AbstractUser):
    """Кастомная модель прользователя."""

    username = models.CharField(
        max_length=constants.USERNAME_MAX_LENGTH,
        unique=True,
        help_text=(
            "Не более 50 знаков. Буквы, цифры и @/./+/-/_"
        ),
        validators=[UnicodeUsernameValidator()],
        error_messages={
            "unique": "Пользователь с таким именем уже сущестует",
        },
        verbose_name='Юзернейм',
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def save(self, *args, **kwargs):
        """При создании пользователя - создается профиль."""
        super().save(*args, **kwargs)
        if not hasattr(self, 'userprofile'):
            UserProfile.objects.create(user=self)


class UserProfile(models.Model):
    """Модель профиля пользователя."""

    user = models.OneToOneField(
        NextgenUser,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
    )
    slug = models.SlugField(
        max_length=constants.SLUG_MAX_LENGTH,
        verbose_name='URL',
    )
    avatar = models.ImageField(
        max_length=constants.PATH_MAX_LENGTH,
        upload_to=file_directory_path,
        default='images/default_user.jpg',
        blank=True,
        validators=[FileExtensionValidator(allowed_extensions=(
            'png', 'jpg', 'jpeg'
        ))],
        verbose_name='Аватар',
    )
    bio = models.TextField(
        max_length=constants.BIO_MAX_LENGTH,
        blank=True,
        verbose_name='О себе',
    )

    class Meta:
        verbose_name = 'Профиль'
        verbose_name_plural = 'Профили'

    def __str__(self):
        return self.user.username

    def save(self, *args, **kwargs):
        """
        При создании новой записи генерируется уникалльынй slug.
        При обновлении фото, старое фото будет удаляться если оно не default.
        """
        if not self.pk:
            self.slug = unique_slugify(self, self.user.username)
        else:
            pre_save_user = self.__class__.objects.get(pk=self.pk)
            if (
                pre_save_user.avatar != self.avatar
                and os.path.isfile(pre_save_user.avatar.path)
                and pre_save_user.avatar.name != 'images/default_user.jpg'
            ):
                os.remove(pre_save_user.avatar.path)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('user_app:profile_detail',
                       kwargs={'username': self.user.username})

    def get_status(self):
        """Получения статуса пользователя из кеша."""
        last_seen = cache.get(f'last-seen-{self.user.id}')

        if last_seen is not None:
            if timezone.now() < (last_seen + timezone.timedelta(seconds=300)):
                return True
        return False
