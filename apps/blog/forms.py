from django import forms

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
        )

    def __init__(self, *args, **kwargs):
        """Обновление стилей в форме."""
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({
                'class': 'form-control',
                'autocomplete': 'off',
            })


class PostUpdateForm(PostCreateForm):
    """Форма для обновления поста."""

    class Meta:
        model = PostCreateForm.Meta.model
        fields = PostCreateForm.Meta.fields + ('fixed',)

    def __init__(self, *args, **kwargs):
        """Обновление стилей в форме."""
        super().__init__(*args, **kwargs)
        self.fields['fixed'].widget.attrs.update({
            'class': 'form-check-input'
        })


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

    class Meta:
        model = Comment
        fields = ('body',)
