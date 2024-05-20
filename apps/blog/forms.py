from django import forms
from django_recaptcha.fields import ReCaptchaField

from .models import Post, Comment


class PostCreateForm(forms.ModelForm):
    """Форма для добавления постов."""

    class Meta:
        model = Post
        fields = (
            'thumbnail',
            'title',
            'description',
            'text',
            'category',
            'fixed',
            'tags',
        )


class PostUpdateForm(PostCreateForm):
    """Форма для обновления поста."""

    class Meta:
        model = PostCreateForm.Meta.model
        fields = PostCreateForm.Meta.fields + ('fixed',)


class CommentCreateForm(forms.ModelForm):
    """Форма для добавления комментария."""

    parent = forms.IntegerField(
        required=False,
        widget=forms.HiddenInput,
    )
    body = forms.CharField(
        label='',
        widget=forms.Textarea(attrs={
            'cols': 30,
            'rows': 5,
            'placeholder': 'Комментарий',
            'class': 'form-control'
        })
    )

    recaptcha = ReCaptchaField(
        label='Капча',
        error_messages={'required': 'Пожалуйста, пройдите капчу'},
    )

    class Meta:
        model = Comment
        fields = ('body',)
