from django.contrib.auth.mixins import AccessMixin
from django.contrib import messages
from django.shortcuts import redirect


class AuthorRequiredMixin(AccessMixin):
    """Миксин: доступы только для автора или персонала."""

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        elif ((request.user != self.get_object().author)
              and not request.user.is_staff):
            messages.info(request,
                          'Редактирование статьи доступно только автору')
            return redirect('blog:home')
        return super().dispatch(request, *args, **kwargs)
