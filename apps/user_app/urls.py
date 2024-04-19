from django.urls import path

from . import views


app_name = 'user_app'

urlpatterns = [
    path('user/edit/',
         views.UserProfileUpdateView.as_view(),
         name='profile_edit'),
    path('user/<slug:username>/',
         views.UserProfileView.as_view(),
         name='profile_detail'),
    path('register/',
         views.UserRegisterView.as_view(),
         name='register'),
    path('login/',
         views.UserLoginView.as_view(),
         name='login'),
    path('logout/',
         views.UserLogoutView.as_view(),
         name='logout'),
]
