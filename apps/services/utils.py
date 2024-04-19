from django.conf import settings

from uuid import uuid4
from pytils.translit import slugify


def unique_slugify(instance, slug: str):
    """Генератор уникальных SLUG."""
    model = instance.__class__
    unique_slug = slugify(slug)
    while model.objects.filter(slug=unique_slug).exists():
        unique_slug = f'{unique_slug}-{uuid4().hex[:8]}'
    return unique_slug


def file_directory_path(instance, filename):
    """
    Формирование директории для сохранения фото.
    Наименование фото генерируется лучайным образом.
    """
    filename = f'{uuid4().hex[:8]}.{filename.split('.')[-1]}'
    path = (f'{settings.MEDIA_ROOT}/images/'
            f'{instance.__class__.__name__}/{instance.slug}/{filename}')
    return path
