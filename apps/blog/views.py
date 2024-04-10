from django.views.generic import ListView, DetailView
from django.shortcuts import get_object_or_404
from django.db.models import Q

from .models import Post, Category


class PostListView(ListView):
    """Страница всех постов."""
    model = Post
    tempalte_name = 'blog/post_list.html'
    context_object_name = 'posts'
    paginate_by = 4

    def get_queryset(self):
        queryset = Post.published.select_related(
            'author',
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
    """Страница конкретного поста"""
    model = Post
    template_name = 'blog/post_detail.html'
    context_object_name = 'post'
    paginate_by = 4

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = self.object.title
        return context


class CategoryListView(ListView):
    """Страница с потами по категориям."""
    template_name = 'blog/post_list.html'
    context_object_name = 'posts'

    def get_queryset(self):
        self.category = get_object_or_404(
            Category,
            slug=self.kwargs.get('slug'),
        )
        sub_cat = Category.objects.filter(parent=self.category)
        queryset = Post.published.select_related(
            'category',
            'author'
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
