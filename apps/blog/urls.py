from django.urls import path

from apps.blog import views


app_name = 'blog'

urlpatterns = [
    path('', views.PostListView.as_view(), name='home'),
    path('post/create/', views.PostCreateView.as_view(), name='post_create'),
    path('post/<slug:slug>/',
         views.PostDetailView.as_view(),
         name='post_detail'),
    path('post/<slug:slug>/delete/',
         views.PostDeleteView.as_view(),
         name='post_delete'),
    path('post/<slug:slug>/update/',
         views.PostUpdateView.as_view(),
         name='post_update'),
    path('post/<int:pk>/comments/create/',
         views.CommentCreateView.as_view(),
         name='comment_create'),
    path('post/<int:pk>/comments/<int:id>/delete/',
         views.CommentDeleteView.as_view(),
         name='comment_delete'),
    path('category/<slug:slug>/',
         views.CategoryListView.as_view(),
         name='category'),
]
