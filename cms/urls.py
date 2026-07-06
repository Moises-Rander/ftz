from django.urls import path

from .views import (
    ConteudoInstitucionalListView,
    DepoimentoListView,
    MembroEquipeListView,
    PostDetailView,
    PostListView,
)

app_name = 'cms'

urlpatterns = [
    path('cms/posts/', PostListView.as_view(), name='posts'),
    path('cms/posts/<slug:slug>/', PostDetailView.as_view(), name='post-detail'),
    path('cms/conteudo/', ConteudoInstitucionalListView.as_view(), name='conteudo'),
    path('cms/equipe/', MembroEquipeListView.as_view(), name='equipe'),
    path('cms/depoimentos/', DepoimentoListView.as_view(), name='depoimentos'),
]
