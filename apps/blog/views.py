from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.contrib import messages
from django.db.models import Q

from .models import Post, Category
from .forms import PostCreateForm, PostUpdateForm
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
    paginate_by = 4
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
