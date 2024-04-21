from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.utils import timezone
from django.utils.deprecation import MiddlewareMixin


NextgenUser = get_user_model()


class ActiveUserMiddleware(MiddlewareMixin):
    def process_request(self, request):
        pass
