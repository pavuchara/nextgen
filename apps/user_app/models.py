from django.contrib.auth.models import AbstractUser


class NextgenUser(AbstractUser):

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
