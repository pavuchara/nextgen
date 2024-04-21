from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.db.models import Q
from django.urls import reverse_lazy
from django.http import JsonResponse
from django.views.generic import (
    View,
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView,
)

from taggit.models import Tag
from .models import Post, Category, Comment, PostRating
from .forms import PostCreateForm, PostUpdateForm, CommentCreateForm
from apps.services.mixins import (
    AuthorRequiredMixin,
    PostListMixin,
    WaringFormMessageMixin,
)


class PostListView(PostListMixin, ListView):
    """Представление: Страница всех постов."""

    tempalte_name = 'blog/post_list.html'

    def get_queryset(self):
        queryset = self.model.published_related.all()
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Главная страница'
        return context


class PostByTagListView(ListView):
    model = Post
    template_name = 'blog/post_list.html'
    context_object_name = 'posts'
    paginate_by = 10
    tag = None

    def get_queryset(self):
        self.tag = Tag.objects.get(slug=self.kwargs['tag'])
        queryset = self.model.published_related.filter(
            tags__slug=self.tag.slug)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Статьи по тегу{self.tag.name}'
        return context


class PostDetailView(DetailView):
    """Представление: конкретный пост."""

    model = Post
    context_object_name = 'post'
    template_name = 'blog/post_detail.html'

    def get_object(self, queryset=None):
        object = get_object_or_404(
            self.model.published.select_related('author', 'category'),
            slug=self.kwargs.get('slug'),
        )
        return object

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            post_rating = PostRating.objects.filter(
                user=self.request.user, post=self.object
            ).first()
            tag_button = post_rating.value if post_rating else None
            context['tag_button'] = tag_button
        context['title'] = self.object.title
        context['form'] = CommentCreateForm()
        return context


class CategoryListView(PostListMixin, ListView):
    """Представление: посты по категориям."""

    template_name = 'blog/post_list.html'

    def get_queryset(self):
        """
        Получает категорию, посты берутся текущей катериии и всех вложенных
        категорий если такие есть.
        """
        self.category = get_object_or_404(
            Category,
            slug=self.kwargs.get('slug'),
        )
        sub_cat = Category.objects.filter(parent=self.category)
        queryset = self.model.published_related.filter(
            (Q(category=self.category) | Q(category__in=sub_cat)),
        ).order_by()
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = self.category.title
        return context


class PostCreateView(LoginRequiredMixin, WaringFormMessageMixin, CreateView):
    """Представление: Создание поста."""

    model = Post
    form_class = PostCreateForm
    template_name = 'blog/post_create.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Новый пост'
        return context

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class PostUpdateView(AuthorRequiredMixin,
                     WaringFormMessageMixin,
                     SuccessMessageMixin,
                     UpdateView):
    """Представление: Обновление материалов в посте."""

    model = Post
    form_class = PostUpdateForm
    template_name = 'blog/post_update.html'
    success_message = 'Запись была успешно обновлена!'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Обновление поста: {self.object.title}'
        return context

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)


class PostDeleteView(AuthorRequiredMixin, DeleteView):
    """Предстваление: Удаление поста."""

    model = Post
    success_url = reverse_lazy('blog:home')
    template_name = 'blog/post_delete.html'


class CommentCreateView(LoginRequiredMixin, CreateView):
    """Предстваление: Добавление комментария."""

    form_class = CommentCreateForm

    def is_ajax(self):
        return self.request.headers.get('X-Requested-With') == 'XMLHttpRequest'

    def form_invalid(self, form):
        if self.is_ajax():
            return JsonResponse({'error': form.errors}, status=400)
        return super().form_invalid(form)

    def form_valid(self, form):
        comment = form.save(commit=False)
        comment.post_id = self.kwargs.get('pk')
        comment.author = self.request.user
        comment.parent_id = form.cleaned_data.get('parent')
        comment.save()

        if self.is_ajax():
            return JsonResponse({
                'is_child': comment.is_child_node(),
                'id': comment.id,
                'author': comment.author.username,
                'parent_id': comment.parent_id,
                'avatar': comment.author.userprofile.avatar.url,
                'body': comment.body,
                'get_absolute_url': comment.author.userprofile.get_absolute_url(),
                'create': comment.create.strftime(
                    '%Y-%b-%d %H:%M:%S'
                ),
            }, status=200)
        return redirect(comment.post.get_absolute_url())

    def handle_no_permission(self):
        return JsonResponse(
            {'error': 'Необходимо авторизоваться для добавления комментариев'},
            status=400
        )


class CommentDeleteView(LoginRequiredMixin, DeleteView):
    """Представление: удаление комментариев."""

    model = Comment
    pk_url_kwarg = 'id'

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.request.user == self.object.author:
            self.object.delete()
            return HttpResponse(status=200)
        else:
            return JsonResponse(
                {'error': 'Вы не имеете права удалять этот комментарий'},
                status=403,
            )


class RatingCreateView(View):
    """Представление: Рейтинг постов."""
    model = PostRating

    def post(self, request, *args, **kwargs):
        user = request.user
        post_id = request.POST.get('pk')
        value = int(request.POST.get('value'))

        rating, created = self.model.objects.get_or_create(
            post_id=post_id,
            user=user,
            defaults={'value': value},
        )

        if not created:
            if rating.value == value:
                rating.delete()
                return JsonResponse({
                    'status': 'deleted',
                    'rating_sum': rating.post.get_sum_rating(),
                })
            else:
                rating.value = value
                rating.save()
                return JsonResponse({
                    'status': 'updated',
                    'rating_sum': rating.post.get_sum_rating(),
                })
        else:
            return JsonResponse({
                'status': 'created',
                'rating_sum': rating.post.get_sum_rating(),
            })
