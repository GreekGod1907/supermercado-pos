from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('pos/', include('pos.urls')),
]

# Servir archivos estáticos en desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    # También incluye STATICFILES_DIRS si existe
    if settings.STATICFILES_DIRS:
        from django.views.static import serve
        import os
        for static_dir in settings.STATICFILES_DIRS:
            urlpatterns += [
                path('static/<path:path>', serve, {'document_root': static_dir}),
            ]