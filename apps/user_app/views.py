from django.db import transaction
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.views.generic import UpdateView, CreateView, ListView

from apps.services.mixins import PostListMixin
from .models import UserProfile
from .forms import (
    UserProfileUpdateForm,
    UserUpdateForm,
    UserRegisterForm,
    UserLoginForm,
)

# Получение модели пользователя.
NextgenUser = get_user_model()


class UserProfileView(PostListMixin, ListView):
    """Представление: Профиль пользователя с его постами."""

    template_name = 'user_app/profile_detail.html'

    def get_queryset(self):
        queryset = self.model.published_related.filter(
            author__username=self.kwargs.get('username'))
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        profile = get_object_or_404(
            UserProfile.objects.select_related('user'),
            user__username=self.kwargs.get('username')
        )
        context['profile'] = profile
        context['title'] = f'Профиль: {self.kwargs.get('username')}'
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
                            f' {self.request.user.username}')
        if self.request.POST:
            context['user_form'] = UserUpdateForm(
                self.request.POST,
                instance=self.request.user,
            )
        else:
            context['user_form'] = UserUpdateForm(
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
            kwargs={'username': self.object.user.username},
        )


class UserRegisterView(SuccessMessageMixin, CreateView):
    """Представление: регистрация пользователя."""

    model = NextgenUser
    form_class = UserRegisterForm
    success_url = reverse_lazy('blog:home')
    template_name = 'user_app/user_register.html'
    success_message = 'Успешная регистрация! Можете авторизоваться на сайте.'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Регистрация'
        return context


class UserLoginView(SuccessMessageMixin, LoginView):
    """Представление: Авторизация пользователя."""

    form_class = UserLoginForm
    next_page = 'blog:home'
    template_name = 'user_app/user_login.html'
    success_message = 'Добро пожаловать!'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Авторизация'
        return context


class UserLogoutView(LogoutView):
    """Представление: Выход из системы."""

    next_page = 'blog:home'
