from django.db import transaction
from django.urls import reverse_lazy
from django.views.generic import DetailView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator

from .models import UserProfile
from .forms import UserProfileUpdateForm, NextgenUserUpdateForm
from apps.blog.models import Post


class UserProfileView(DetailView):
    """Представление: Профиль пользователя с его постами."""

    model = UserProfile
    template_name = 'user_app/profile_detail.html'
    context_object_name = 'profile'

    def get_queryset(self):
        queryset = UserProfile.objects.select_related('user')
        return queryset

    def get_context_data(self, **kwargs):
        """Получение пользователя и его постов."""
        context = super().get_context_data(**kwargs)
        posts = Post.published.select_related(
            'author',
            'author__userprofile',
            'category',
        ).filter(author__username=self.object)
        paginator_context = self.paginate_user_posts(posts)
        context.update(paginator_context)
        context['title'] = f'Профиль: {self.object}'
        return context

    def paginate_user_posts(self, posts):
        """Метод пагинации."""
        page_number = self.request.GET.get('page', 1)
        paginator = Paginator(posts, 2)
        posts = paginator.get_page(page_number)
        context = {
            'paginator': paginator,
            'is_paginated': True,
            'paginator_range': paginator.page_range,
            'posts': posts,
        }
        if paginator.num_pages < 2:
            context['is_paginated'] = False
        return context


class UserProfileUpdateView(LoginRequiredMixin, UpdateView):
    """Представление: Редактирование профиля пользователя."""

    model = UserProfile
    template_name = 'user_app/update_profile.html'
    form_class = UserProfileUpdateForm

    def get_object(self, queryset=None):
        return self.request.user.userprofile

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = (f'Редактирование профиля пользователя'
                            f'{self.request.user.username}')
        if self.request.POST:
            context['user_form'] = NextgenUserUpdateForm(
                self.request.POST,
                instance=self.request.user,
            )
        else:
            context['user_form'] = NextgenUserUpdateForm(
                instance=self.request.user,
            )
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        user_form = context['user_form']
        with transaction.atomic():
            if all([form.is_valid(), user_form.is_valid()]):
                user_form.save()
                form.save()
            else:
                context.update({'user_form': user_form})
                return self.render_to_response(context)
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy(
            'user_app:profile_detail',
            kwargs={'slug': self.request.user.userprofile.slug},
        )
