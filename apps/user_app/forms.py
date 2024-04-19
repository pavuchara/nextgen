from django import forms
from django.core.validators import FileExtensionValidator
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django_recaptcha.fields import ReCaptchaField

from .models import UserProfile


# Получение модели пользователя.
NextgenUser = get_user_model()


class UserUpdateForm(forms.ModelForm):
    """Форма: обновления данных пользователя."""

    class Meta:
        model = NextgenUser
        fields = ('username', 'email', 'first_name', 'last_name')


class UserProfileUpdateForm(forms.ModelForm):
    """Форма: обновление профиля пользователя."""

    avatar = forms.ImageField(
        required=False,
        validators=[FileExtensionValidator(allowed_extensions=(
            'png', 'jpg', 'jpeg',
        ))],
        label='Аватар',
    )

    # recaptcha = ReCaptchaField(
    #     label='Капча',
    #     error_messages={'required': 'Пожалуйста, пройдите капчу'},
    # )

    class Meta:
        model = UserProfile
        fields = ('avatar', 'bio')


class UserRegisterForm(UserCreationForm):
    """Форма: регистрация пользователя."""

    recaptcha = ReCaptchaField(
        label='Капча',
        error_messages={'required': 'Пожалуйста, пройдите капчу'},
    )

    class Meta(UserCreationForm.Meta):
        model = NextgenUser
        fields = UserCreationForm.Meta.fields + (
            'email', 'first_name', 'last_name')


class UserLoginForm(AuthenticationForm):
    """Форма авторизации на сайте."""

    recaptcha = ReCaptchaField(
        label='Капча',
        error_messages={'required': 'Пожалуйста, пройдите капчу'},
    )
