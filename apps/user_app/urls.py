from django.urls import path


from .views import UserProfileView, UserProfileUpdateView


app_name = 'user_app'

urlpatterns = [
    path('user/edit/', UserProfileUpdateView.as_view(), name='profile_edit'),
    path('user/<slug:slug>/',
         UserProfileView.as_view(),
         name='profile_detail'),
]
