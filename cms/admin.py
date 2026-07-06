from django.contrib import admin

from .models import ConteudoInstitucional, Depoimento, MembroEquipe, Post


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'slug', 'categoria', 'data_publicacao', 'is_publicado')
    list_filter = ('is_publicado', 'categoria', 'data_publicacao')
    search_fields = ('titulo', 'conteudo', 'categoria')
    list_editable = ('is_publicado',)
    date_hierarchy = 'data_publicacao'
    prepopulated_fields = {'slug': ('titulo',)}


@admin.register(ConteudoInstitucional)
class ConteudoInstitucionalAdmin(admin.ModelAdmin):
    list_display = ('secao', 'titulo', 'ordem', 'is_ativo')
    list_filter = ('secao', 'is_ativo')
    search_fields = ('titulo', 'texto')
    list_editable = ('ordem', 'is_ativo')


@admin.register(MembroEquipe)
class MembroEquipeAdmin(admin.ModelAdmin):
    list_display = ('nome', 'cargo', 'ordem', 'is_ativo')
    list_filter = ('is_ativo',)
    search_fields = ('nome', 'cargo', 'bio')
    list_editable = ('ordem', 'is_ativo')


@admin.register(Depoimento)
class DepoimentoAdmin(admin.ModelAdmin):
    list_display = ('nome_aluno', 'nome_curso', 'ordem', 'is_publicado')
    list_filter = ('is_publicado',)
    search_fields = ('nome_aluno', 'nome_curso', 'texto')
    list_editable = ('ordem', 'is_publicado')
