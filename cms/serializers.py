from django.utils.text import Truncator
from rest_framework import serializers

from .models import ConteudoInstitucional, Depoimento, MembroEquipe, Post


class PostListSerializer(serializers.ModelSerializer):
    resumo = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = (
            'id', 'titulo', 'slug', 'categoria', 'imagem', 'resumo', 'data_publicacao',
        )

    def get_resumo(self, obj):
        return Truncator(obj.conteudo or '').chars(200)


class PostDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = (
            'id', 'titulo', 'slug', 'conteudo', 'imagem', 'categoria', 'data_publicacao',
        )


class ConteudoInstitucionalSerializer(serializers.ModelSerializer):
    secao_display = serializers.CharField(source='get_secao_display', read_only=True)

    class Meta:
        model = ConteudoInstitucional
        fields = ('id', 'secao', 'secao_display', 'titulo', 'texto', 'imagem', 'ordem')


class MembroEquipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = MembroEquipe
        fields = ('id', 'nome', 'cargo', 'bio', 'foto', 'ordem')


class DepoimentoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Depoimento
        fields = ('id', 'nome_aluno', 'foto', 'nome_curso', 'texto', 'ordem')
