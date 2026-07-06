from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.permissions import AllowAny

from .models import ConteudoInstitucional, Depoimento, MembroEquipe, Post
from .serializers import (
    ConteudoInstitucionalSerializer,
    DepoimentoSerializer,
    MembroEquipeSerializer,
    PostDetailSerializer,
    PostListSerializer,
)


class PostListView(ListAPIView):
    """Posts publicados, com filtro opcional por categoria."""

    permission_classes = (AllowAny,)
    serializer_class = PostListSerializer

    def get_queryset(self):
        qs = Post.objects.filter(is_publicado=True)
        categoria = self.request.query_params.get('categoria')
        if categoria:
            qs = qs.filter(categoria__iexact=categoria)
        return qs.order_by('-data_publicacao')


class PostDetailView(RetrieveAPIView):
    """Detalhe de um post publicado, por slug."""

    permission_classes = (AllowAny,)
    serializer_class = PostDetailSerializer
    lookup_field = 'slug'
    queryset = Post.objects.filter(is_publicado=True)


class ConteudoInstitucionalListView(ListAPIView):
    """Conteúdo institucional ativo, com filtro opcional por seção."""

    permission_classes = (AllowAny,)
    serializer_class = ConteudoInstitucionalSerializer

    def get_queryset(self):
        qs = ConteudoInstitucional.objects.filter(is_ativo=True)
        secao = self.request.query_params.get('secao')
        if secao:
            qs = qs.filter(secao=secao.upper())
        return qs.order_by('secao', 'ordem')


class MembroEquipeListView(ListAPIView):
    """Membros da equipe ativos, ordenados por ``ordem``."""

    permission_classes = (AllowAny,)
    serializer_class = MembroEquipeSerializer
    queryset = MembroEquipe.objects.filter(is_ativo=True).order_by('ordem', 'nome')


class DepoimentoListView(ListAPIView):
    """Depoimentos publicados, ordenados por ``ordem``."""

    permission_classes = (AllowAny,)
    serializer_class = DepoimentoSerializer
    queryset = Depoimento.objects.filter(is_publicado=True).order_by('ordem', 'nome_aluno')
