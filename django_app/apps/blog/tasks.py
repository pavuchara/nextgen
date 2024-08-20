import logging
from uuid import uuid4

from django.db import transaction
from django.contrib.auth import get_user_model

from blog_nextgen.celery import app
from apps.blog.models import PostRating, Post


UserModel = get_user_model()


logger = logging.getLogger(__name__)


@app.task
def autolike_post_every_5_seconds():
    """Создает рандомного пользователя и ставит лайк рандомному посту."""
    try:
        with transaction.atomic():
            # Создание пользователя
            user = UserModel.objects.create_user(
                username=str(uuid4())[:5],
                password=str(uuid4())[:5],
            )
            logger.info(f"Создан пользователь: {user.username}")

            # Выбор случайного поста
            random_post = Post.published.order_by('?').first()
            if not random_post:
                logger.warning("Не удалось найти опубликованные посты.")
                return

            # Ставим лайк посту
            PostRating.objects.create(
                post=random_post,
                user=user,
                value=1,
            )
            logger.info(f"Пользователь {user.username} поставил лайк посту {random_post.id}")

    except Exception as e:
        logger.error(f"Ошибка при выполнении задачи: {str(e)}")
