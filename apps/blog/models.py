from django.db import models
from django.urls import reverse
from django.core.validators import FileExtensionValidator
from django.contrib.auth import get_user_model
from taggit.managers import TaggableManager
from ckeditor.fields import RichTextField
from django.db.models import Sum

import os
from apps.services import constants
from mptt.models import MPTTModel, TreeForeignKey
from apps.services.utils import unique_slugify, file_directory_path

# Получение модели пользователя.
NextgenUser = get_user_model()


class PostPublishedManager(models.Manager):
    """Модельный менеджер для опубликованых постов."""
    def get_queryset(self):
        return super().get_queryset().filter(status='published')


class PostPublishedRealtedManager(PostPublishedManager):
    """
    Модельный менеджер для опубликованых постов со связанными полями.
    Аннотированы кол-вом лайков и отсортированы по дате создания.
    """

    def get_queryset(self):
        queryset = super().get_queryset().select_related(
            'author',
            'author__userprofile',
            'category',
        ).prefetch_related('tags').annotate(
            get_sum_rating=Sum('ratings__value')).order_by('-create')
        return queryset


class Post(models.Model):
    """Модель: Пост."""

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
    description = RichTextField(
        config_name='awesome_ckeditor',
        max_length=constants.DESC_MAX_LENGTH,
        verbose_name='Краткое описание',
    )
    text = RichTextField(
        config_name='awesome_ckeditor',
        verbose_name='Полное описание',
    )
    category = TreeForeignKey(
        'Category',
        on_delete=models.PROTECT,
        related_name='posts',
        verbose_name='Категория',
    )
    thumbnail = models.ImageField(
        max_length=constants.PATH_MAX_LENGTH,
        upload_to=file_directory_path,
        default='default_post.jpg',
        blank=True,
        validators=[FileExtensionValidator(allowed_extensions=(
            'png', 'jpg', 'webp', 'jpeg', 'gif'
        ))],
        verbose_name='Изображение поста',
    )
    tags = TaggableManager(
        verbose_name='Теги',
        help_text='Список тегов, разделенный запятыми.',
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
    published_related = PostPublishedRealtedManager()

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
        При создании новой записи генерируется уникалльный slug, если он
        совпадает с тем что уже есть.
        При обновлении фото, старое будет удаляться.
        """
        if not self.pk:
            self.slug = unique_slugify(self, self.title)
        else:
            old_post = Post.objects.get(pk=self.pk)
            if (old_post.thumbnail != self.thumbnail
                    and os.path.isfile(old_post.thumbnail.path)):
                os.remove(old_post.thumbnail.path)
        super().save(*args, **kwargs)

    def get_sum_rating(self):
        return sum((rating.value for rating in self.ratings.all()))


class Category(MPTTModel):
    """Модель: Древовидные категорий с вложенностью."""

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


class Comment(MPTTModel):
    """Модель: Древовыидные комментарии."""

    STATUS_OPTIONS = (
        ('published', 'Опубликовано'),
        ('draft', 'Черновик')
    )

    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Пост',
    )
    author = models.ForeignKey(
        NextgenUser,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Автор',
    )
    status = models.CharField(
        max_length=10,
        choices=STATUS_OPTIONS,
        default='published',
        verbose_name='Статус',
    )
    create = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Время добавления'
    )
    body = models.TextField(
        null=False,
        blank=False,
        max_length=constants.COMM_MAX_LENGTH,

    )
    parent = TreeForeignKey(
        'self',
        null=True,
        blank=True,
        related_name='children',
        on_delete=models.CASCADE,
        verbose_name='Родительский комментарий',
    )

    class MTTMeta:
        order_insertion_by = ('-create',)

    class Meta:
        ordering = ('-create',)
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'

    def __str__(self):
        return f'{self.author}:{self.body}'


class PostRating(models.Model):
    """Модель: Рейтинг постов."""

    post = models.ForeignKey(
        to=Post,
        on_delete=models.CASCADE,
        related_name='ratings',
        verbose_name='Запись',
    )
    user = models.ForeignKey(
        to=NextgenUser,
        on_delete=models.CASCADE,
        related_name='ratings',
        verbose_name='Пользователь',
    )
    value = models.IntegerField(
        choices=[(1, 'Нравится'), (-1, 'Не нравится')],
        verbose_name='Значение',
    )

    class Meta:
        unique_together = ('post', 'user')
        indexes = [models.Index(fields=['value'])]
        verbose_name = 'Рейтинг'
        verbose_name_plural = 'Рейтинги'

    def __str__(self):
        return self.post.title
