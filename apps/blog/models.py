from django.db import models
from django.core.validators import FileExtensionValidator
from apps.user_app.models import NextgenUser


class Post(models.Model):
    """Модель поста"""

    STATUS_OPTIONS = (
        ('published', 'Опубликовано'),
        ('draft', 'Черновик')
    )

    title = models.CharField(max_length=255, verbose_name='Заголовок')
    slug = models.SlugField(
        max_length=255,
        blank=True,
        unique=True,
        verbose_name='URL',
    )
    description = models.TextField(
        max_length=500,
        verbose_name='Краткое описание',
    )
    text = models.TextField(verbose_name='Полное описание')
    thumbnail = models.ImageField(
        default='default_post.jpg',
        blank=True,
        upload_to='images/thumbnails',
        validators=[FileExtensionValidator(allowed_extensions=(
            'png', 'jpg', 'webp', 'jpeg', 'gif'
        ))],
        verbose_name='Изображение поста',
    )
    status = models.CharField(
        max_length=10,
        choices=STATUS_OPTIONS,
        default='published',
        verbose_name='Статус',
    )
    create = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Время добавления',
    )
    update = models.DateTimeField(
        auto_now=True,
        verbose_name='Время обновления',
    )
    author = models.ForeignKey(
        to=NextgenUser,
        default=1,
        on_delete=models.SET_DEFAULT,
        related_name='author_posts',
        verbose_name='Автор',
    )
    updater = models.ForeignKey(
        to=NextgenUser,
        default=1,
        on_delete=models.SET_DEFAULT,
        related_name='updater_posts',
        verbose_name='Обновил',
    )
    fixed = models.BooleanField(default=False, verbose_name='Закреплено')

    class Meta:
        ordering = ['-fixed', '-create']
        indexes = [models.Index(fields=['-fixed', '-create', 'status'])]
        verbose_name = 'Статья'
        verbose_name_plural = 'Статьи'

    def __str__(self):
        return self.title
