from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.utils import timezone
from django.utils.deprecation import MiddlewareMixin


NextgenUser = get_user_model()


class ActiveUserMiddleware(MiddlewareMixin):
    """
    Jбновления статуса "онлайн" пользователя в Django
    с помощью кэширования.
    Если пользователь авторизован и имеет уникальный session_key, то
    обновляется его статус "последний раз в сети" с помощью метода cache.set()
    и сохраняется в кэше на время 300 секунд.
    """
    def process_request(self, request):
        if request.user.is_authenticated and request.session.session_key:
            cache_key = f'last-seen-{request.user.id}'
            last_login = cache.get(cache_key)

            if not last_login:
                NextgenUser.objects.filter(id=request.user.id).update(
                    last_login=timezone.now())
                cache.set(cache_key, timezone.now(), 300)
