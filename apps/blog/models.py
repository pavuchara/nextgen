from django.db import models
from django.urls import reverse
from django.core.validators import FileExtensionValidator

import os
from apps import constants
from mptt.models import MPTTModel, TreeForeignKey
from apps.user_app.models import NextgenUser
from apps.services.utils import unique_slugify, file_directory_path


class PostPublishedManager(models.Manager):
    """Модельный менеджер для опубликованых постов."""
    def get_queryset(self):
        return super().get_queryset().filter(status='published')


class Post(models.Model):
    """Модель поста."""

    STATUS_OPTIONS = (
        ('published', 'Опубликовано'),
        ('draft', 'Черновик')
    )

    title = models.CharField(
        max_length=constants.TITLE_MAX_LENGTH,
        verbose_name='Заголовок',
    )
    slug = models.SlugField(
        unique=True,
        max_length=constants.SLUG_MAX_LENGTH,
        verbose_name='URL',
    )
    description = models.TextField(
        max_length=constants.DESC_MAX_LENGTH,
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
        max_length=1000,
        upload_to=file_directory_path,
        default='default_post.jpg',
        blank=True,
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

    objects = models.Manager()
    published = PostPublishedManager()

    class Meta:
        db_table = 'blog_post'
        ordering = ['-fixed', '-create']
        indexes = [models.Index(fields=['-fixed', '-create', 'status'])]
        verbose_name = 'Статья'
        verbose_name_plural = 'Статьи'

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('blog:post_detail', kwargs={'slug': self.slug})

    def save(self, *args, **kwargs):
        """
        При создании новой записи генерируется уникалльный slug,
        дополнительно старое фото будет удаляться.
        """
        if not self.pk:
            self.slug = unique_slugify(self, self.title)
        else:
            old_post = Post.objects.get(pk=self.pk)
            if (old_post.thumbnail != self.thumbnail
                    and os.path.isfile(old_post.thumbnail.path)):
                os.remove(old_post.thumbnail.path)
        super().save(*args, **kwargs)


class Category(MPTTModel):
    """Древовидная модель категорий с вложенностью."""

    title = models.CharField(
        max_length=constants.TITLE_MAX_LENGTH,
        verbose_name='Категоия'
    )
    slug = models.SlugField(
        unique=True,
        max_length=constants.SLUG_MAX_LENGTH,
        verbose_name='URL категории',
    )
    description = models.TextField(
        max_length=constants.DESC_MAX_LENGTH,
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

    def get_absolute_url(self):
        return reverse('blog:category', kwargs={'slug': self.slug})
