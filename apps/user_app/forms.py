from django import forms
from django.core.validators import FileExtensionValidator
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm

from .models import UserProfile


# Получение модели пользователя.
NextgenUser = get_user_model()


class UserUpdateForm(forms.ModelForm):
    """Форма: обновления данных пользователя."""

    class Meta:
        model = NextgenUser
        fields = ('username', 'email', 'first_name', 'last_name')

    def clean_email(self):
        """Проверка E-mail на уникальнсоть."""
        email = self.cleaned_data.get('email')
        username = self.cleaned_data.get('username')
        if email and NextgenUser.objects.filter(
                email=email).exclude(username=username).exists():
            raise forms.ValidationError('Пользователь с таким E-mail '
                                        'уже зарегистрирован')


class UserProfileUpdateForm(forms.ModelForm):
    """Форма: обновление профиля пользователя."""

    avatar = forms.ImageField(
        required=False,
        validators=[FileExtensionValidator(allowed_extensions=(
            'png', 'jpg', 'jpeg',
        ))],
        label='Аватар',
    )

    class Meta:
        model = UserProfile
        fields = ('avatar', 'bio')


class UserRegisterForm(UserCreationForm):
    """Форма: регистрация пользователя."""

    class Meta(UserCreationForm.Meta):
        model = NextgenUser
        fields = UserCreationForm.Meta.fields + (
            'email', 'first_name', 'last_name')

    def clean_email(self):
        """Проверка E-mail на уникальность."""
        email = self.cleaned_data.get('email')
        username = self.cleaned_data.get('username')
        if email and NextgenUser.objects.filter(
             email=email).exclude(username=username).exists():
            raise forms.ValidationError(
                'Пользователь с таким E-mail уже есть в системе.'
            )
        return email


class UserLoginForm(AuthenticationForm):
    """Форма авторизации на сайте."""

    pass
