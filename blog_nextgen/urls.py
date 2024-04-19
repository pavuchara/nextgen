from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('apps.blog.urls', namespace='blog')),
    path('', include('apps.user_app.urls', namespace='user_app')),
    path('ckeditor/', include('ckeditor_uploader.urls')),
]

if settings.DEBUG is True:
    import debug_toolbar
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT,
    )
    urlpatterns += (path('__debug__/', include(debug_toolbar.urls)), )
