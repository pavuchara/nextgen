import os
from datetime import timedelta

from celery import Celery


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'blog_nextgen.settings')
app = Celery('blog_nextgen', broker_connection_retry=False, broker_connection_retry_on_startup=True)
app.config_from_object('django.conf:settings')

app.autodiscover_tasks()

app.conf.beat_schedule = {
    "autolike_post_every_5_seconds": {
        "task": "apps.blog.tasks.autolike_post_every_5_seconds",
        "schedule": timedelta(seconds=20),
    },
}
