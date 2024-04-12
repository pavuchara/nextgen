from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.db.models import Q
from django.http import JsonResponse

from .models import Post, Category, Comment
from .forms import PostCreateForm, PostUpdateForm, CommentCreateForm
from apps.services.mixins import AuthorRequiredMixin


class PostListView(ListView):
    """Представление: Страница всех постов."""

    model = Post
    paginate_by = 4
    context_object_name = 'posts'
    tempalte_name = 'blog/post_list.html'

    def get_queryset(self):
        queryset = Post.published.select_related(
            'author',
            'author__userprofile',
            'category',
        )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Главная страница'
        page = context.get('page_obj')
        if page:
            context['paginator_range'] = page.paginator.get_elided_page_range(
                page.number,
                on_each_side=1,
                on_ends=1
            )
        return context


class PostDetailView(DetailView):
    """Представление: конкретный пост."""

    model = Post
    context_object_name = 'post'
    template_name = 'blog/post_detail.html'

    def get_queryset(self):
        queryset = Post.published.select_related(
            'author',
        )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = self.object.title
        context['form'] = CommentCreateForm
        return context


class CategoryListView(ListView):
    """Представление: посты по категориям."""

    context_object_name = 'posts'
    template_name = 'blog/post_list.html'

    def get_queryset(self):
        self.category = get_object_or_404(
            Category,
            slug=self.kwargs.get('slug'),
        )
        sub_cat = Category.objects.filter(parent=self.category)
        queryset = Post.published.select_related(
            'category',
            'author',
            'author__userprofile'
        ).filter(
            (Q(category=self.category) | Q(category__in=sub_cat)),
        ).order_by()
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = self.category.title
        page = context.get('page_obj')
        if page:
            context['paginator_range'] = page.paginator.get_elided_page_range(
                page.number,
                on_each_side=1,
                on_ends=1
            )
        return context


class PostCreateView(LoginRequiredMixin, CreateView):
    """Представление: Создание поста."""

    model = Post
    form_class = PostCreateForm
    template_name = 'blog/post_create.html'
    login_url = 'blog:home'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Новый пост'
        return context

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.info(request,
                          'Для создания записи, необходимо авторизироваться')
            return redirect('user_app:login')
        return super().dispatch(request, *args, **kwargs)


class PostUpdateView(AuthorRequiredMixin, SuccessMessageMixin, UpdateView):
    """Представление: Обновление материалов в посте."""

    model = Post
    form_class = PostUpdateForm
    context_object_name = 'post'
    template_name = 'blog/post_update.html'
    success_message = 'Запись была успешно обновлена!'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Обновление поста: {self.object.title}'
        return context

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)


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


class CommentDeleteView(LoginRequiredMixin, SuccessMessageMixin, DeleteView):

    model = Comment
    success_message = 'Комментарий удален!'
    pk_url_kwarg = 'id'

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.request.user == self.object.author:
            self.object.delete()
            return JsonResponse({'message': self.success_message}, status=200)
        else:
            return JsonResponse(
                {'error': 'Вы не имеете права удалять этот комментарий'},
                status=403,
            )
