from django.db import models
from django.core.validators import FileExtensionValidator

from apps.user_app.models import NextgenUser
from mptt.models import MPTTModel, TreeForeignKey
from apps import constants


class Post(models.Model):
    """Модель поста."""

    STATUS_OPTIONS = (
        ('published', 'Опубликовано'),
        ('draft', 'Черновик')
    )

    title = models.CharField(
        max_length=constants.MAX_LENGTH,
        verbose_name='Заголовок',
    )
    slug = models.SlugField(
        max_length=constants.MAX_LENGTH,
        blank=True,
        unique=True,
        verbose_name='URL',
    )
    description = models.TextField(
        max_length=500,
        verbose_name='Краткое описание',
    )
    text = models.TextField(verbose_name='Полное описание')
    category = TreeForeignKey(
        'Category',
        on_delete=models.PROTECT,
        related_name='posts',
        verbose_name='Категория',
    )
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
        db_table = 'blog_post'
        ordering = ['-fixed', '-create']
        indexes = [models.Index(fields=['-fixed', '-create', 'status'])]
        verbose_name = 'Статья'
        verbose_name_plural = 'Статьи'

    def __str__(self):
        return self.title


class Category(MPTTModel):
    """Древовидная модель категорий с вложенностью."""
    title = models.CharField(
        max_length=constants.MAX_LENGTH,
        verbose_name='Категоия'
    )
    slug = models.SlugField(
        max_length=constants.MAX_LENGTH,
        verbose_name='URL категории',
    )
    description = models.TextField(
        max_length=300,
        verbose_name='Описание категории',
    )
    parent = TreeForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        db_index=True,
        related_name='children',
        verbose_name='Родительская категория',
    )

    class MPTTMeta:
        """Сортировка по вложенности."""
        order_insertion_by = ('title',)

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
        db_table = 'app_categories'

    def __str__(self):
        return self.title
