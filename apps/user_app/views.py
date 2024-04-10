from django.db import transaction
from django.urls import reverse_lazy
from django.views.generic import DetailView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin

from .models import UserProfile
from .forms import UserProfileUpdateForm, NextgenUserUpdateForm


class UserProfileView(DetailView):
    model = UserProfile
    template_name = 'user_app/profile_detail.html'
    context_object_name = 'profile'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = (f'Профиль пользователя: '
                            f'{self.request.user.username}')
        return context


class UserProfileUpdateView(LoginRequiredMixin, UpdateView):
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
