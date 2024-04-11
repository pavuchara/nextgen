from django import forms
from django.core.validators import FileExtensionValidator
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm

from .models import NextgenUser, UserProfile
from apps import constants


class UserUpdateForm(forms.ModelForm):
    """Форма: обновления данных пользователя."""

    username = forms.CharField(
        required=False,
        max_length=constants.USERNAME_MAX_LENGTH,
        widget=forms.TextInput(attrs={
            'class': 'form-control mb-1',
            'placeholder': 'Username',
        })
    )
    email = forms.EmailField(
        required=False,
        widget=forms.EmailInput(attrs={
           'class': 'form-control mb-1',
           'placeholder': 'E-mail',
        }),
    )
    first_name = forms.CharField(
        required=False,
        max_length=constants.NAME_MAX_LENGTH,
        widget=forms.TextInput(attrs={
            'class': 'form-control mb-1',
            'placeholder': 'Имя',
        }),
    )
    last_name = forms.CharField(
        required=False,
        max_length=constants.NAME_MAX_LENGTH,
        widget=forms.TextInput(attrs={
            'class': 'form-control mb-1',
            'placeholder': 'Фамилия',
        }),
    )

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
        widget=forms.FileInput(attrs={
            'class': 'form-control mb-1',
        }),
    )
    bio = forms.CharField(
        max_length=constants.DESC_MAX_LENGTH,
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control mb-1',
            'rows': 5,
            'placeholder': 'О себе',
        }),
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

    def __init__(self, *args, **kwargs):
        """Обновление стилей в форме."""
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({"placeholder": "Логин"})
        self.fields['email'].widget.attrs.update({"placeholder": "E-mail"})
        self.fields['first_name'].widget.attrs.update({"placeholder": "Имя"})
        self.fields['last_name'].widget.attrs.update(
            {"placeholder": "Фамилия"}
        )
        self.fields['password1'].widget.attrs.update({"placeholder": "Пароль"})
        self.fields['password2'].widget.attrs.update(
            {"placeholder": "Повторите пароль"}
        )
        for field in self.fields:
            self.fields[field].widget.attrs.update({
                "class": "form-control", "autocomplete": "off"
            })


class UserLoginForm(AuthenticationForm):
    """Форма авторизации на сайте."""

    def __init__(self, *args, **kwargs):
        """Обновление стилей в форме."""
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs['placeholder'] = 'Логин'
        self.fields['password'].widget.attrs['placeholder'] = 'Пароль'
        self.fields['username'].label = 'Логин'
        for field in self.fields:
            self.fields[field].widget.attrs.update({
                'class': 'form-control',
                'autocomplite': 'off',
            })
