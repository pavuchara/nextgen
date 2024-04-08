from django.urls import path

from apps.blog import views


app_name = 'blog'

urlpatterns = [
    path('', views.PostListView.as_view(), name='home'),
    path(
        'post/<slug:slug>/',
        views.PostDetailView.as_view(),
        name='post_detail'
    ),
    path(
        'category/<slug:slug>/',
        views.CategoryListView.as_view(),
        name='category'
    ),
]
