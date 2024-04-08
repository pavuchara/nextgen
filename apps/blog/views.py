from django.views.generic import ListView, DetailView
from django.shortcuts import get_object_or_404
from django.db.models import Q

from .models import Post, Category


class PostListView(ListView):
    model = Post
    tempalte_name = 'blog/post_list.html'
    context_object_name = 'posts'

    def get_queryset(self):
        queryset = Post.objects.select_related(
            'author',
            'category',
        ).filter(status='published')
        return queryset


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Главная страница'
        return context





class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/post_detail.html'
    context_object_name = 'post'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = self.object.title
        return context


class CategoryListView(ListView):
    category = None
    template_name = 'blog/post_list.html'
    context_object_name = 'posts'

    def get_queryset(self):
        self.category = get_object_or_404(
            Category,
            slug=self.kwargs.get('slug'),
        )
        sub_cat = Category.objects.filter(parent=self.category)
        queryset = Post.objects.select_related(
            'category',
            'author'
        ).filter(
            (Q(category=self.category) | Q(category__in=sub_cat)),
            status='published',
        ).order_by()
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = self.category.title
        return context
