from django.contrib.auth.mixins import AccessMixin
from django.contrib import messages
from django.shortcuts import redirect

from apps.blog.models import Post
from apps.services.constants import PAGINATE_POSTS_COUNT


class AuthorRequiredMixin(AccessMixin):
    """Миксин: доступы только для автора или персонала."""

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        elif ((request.user != self.get_object().author)
              and not request.user.is_staff):
            messages.info(request,
                          'Редактирование доступно только автору')
            return redirect('blog:home')
        return super().dispatch(request, *args, **kwargs)


class PostListMixin:
    """Миксин: Модель поста с пагинацией и шаблоном."""

    model = Post
    paginate_by = PAGINATE_POSTS_COUNT
    context_object_name = 'posts'
    tempalte_name = 'blog/post_list.html'


class WaringFormMessageMixin:
    """Миксин: Вывод информации об ошибке в форме."""

    def form_invalid(self, form):
        messages.add_message(
            self.request, messages.WARNING, form.errors.as_text()
        )
        return super().form_invalid(form)
