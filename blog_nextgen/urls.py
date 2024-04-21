from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static


handler403 = 'apps.core.views.custom_403'
handler404 = 'apps.core.views.custom_404'
handler500 = 'apps.core.views.custom_500'


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('apps.blog.urls', namespace='blog')),
    path('', include('apps.user_app.urls', namespace='user_app')),
    path('ckeditor/', include('ckeditor_uploader.urls')),
    re_path(r'^oauth/', include('social_django.urls', namespace='social')),
]

if settings.DEBUG is True:
    import debug_toolbar
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT,
    )
    urlpatterns += (path('__debug__/', include(debug_toolbar.urls)), )
