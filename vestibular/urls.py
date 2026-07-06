from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import CandidatoAdminViewSet, EdicaoAdminViewSet, EdicaoPublicViewSet

app_name = 'vestibular'

public_router = DefaultRouter()
public_router.register('edicoes', EdicaoPublicViewSet, basename='edicao')

admin_router = DefaultRouter()
admin_router.register('edicoes', EdicaoAdminViewSet, basename='admin-edicao')
admin_router.register('candidatos', CandidatoAdminViewSet, basename='admin-candidato')

urlpatterns = [
    path('vestibular/', include((public_router.urls, 'public'))),
    path('admin/vestibular/', include((admin_router.urls, 'adm'))),
]
