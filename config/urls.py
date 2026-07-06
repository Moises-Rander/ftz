"""URL configuration for the FTZ project."""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

admin.site.site_header = 'Faculdade de Teologia Zait'
admin.site.site_title = 'FTZ Admin'
admin.site.index_title = 'Administração'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('accounts.urls')),
    path('api/', include('cursos.urls')),
    path('api/', include('matriculas.urls')),
    path('api/', include('vestibular.urls')),
    path('api/', include('academico.urls')),
    path('api/', include('cms.urls')),
]

# Servir arquivos de mídia em desenvolvimento
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
