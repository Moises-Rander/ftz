from django.contrib import admin

from .models import (
    Aula,
    Avaliacao,
    EntregaTrabalho,
    Frequencia,
    ResultadoAvaliacao,
    Trabalho,
)


class FrequenciaInline(admin.TabularInline):
    model = Frequencia
    extra = 0
    autocomplete_fields = ('aluno', 'lancado_por')


@admin.register(Aula)
class AulaAdmin(admin.ModelAdmin):
    list_display = ('data', 'horario_inicio', 'turma', 'disciplina', 'modulo', 'cancelada')
    list_filter = ('cancelada', 'data', 'turma', 'turma__curso__tipo')
    search_fields = ('turma__nome', 'disciplina__nome', 'modulo__nome')
    autocomplete_fields = ('turma', 'disciplina', 'modulo', 'ciclo')
    inlines = (FrequenciaInline,)


@admin.register(Frequencia)
class FrequenciaAdmin(admin.ModelAdmin):
    list_display = ('aluno', 'aula', 'presente', 'lancado_por')
    list_filter = ('presente', 'aula__turma')
    search_fields = ('aluno__user__email', 'aluno__cpf', 'aula__turma__nome')
    autocomplete_fields = ('aula', 'aluno', 'lancado_por')


class ResultadoAvaliacaoInline(admin.TabularInline):
    model = ResultadoAvaliacao
    extra = 0
    autocomplete_fields = ('aluno', 'lancado_por')


@admin.register(Avaliacao)
class AvaliacaoAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'turma', 'disciplina', 'modulo', 'data', 'nota_maxima')
    list_filter = ('data', 'turma', 'turma__curso__tipo')
    search_fields = ('titulo', 'turma__nome', 'disciplina__nome', 'modulo__nome')
    autocomplete_fields = ('turma', 'disciplina', 'modulo')
    inlines = (ResultadoAvaliacaoInline,)


@admin.register(ResultadoAvaliacao)
class ResultadoAvaliacaoAdmin(admin.ModelAdmin):
    list_display = ('avaliacao', 'aluno', 'nota', 'lancado_por')
    list_filter = ('avaliacao__turma',)
    search_fields = ('aluno__user__email', 'aluno__cpf', 'avaliacao__titulo')
    autocomplete_fields = ('avaliacao', 'aluno', 'lancado_por')


class EntregaTrabalhoInline(admin.TabularInline):
    model = EntregaTrabalho
    extra = 0
    readonly_fields = ('data_hora_entrega',)
    autocomplete_fields = ('aluno',)


@admin.register(Trabalho)
class TrabalhoAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'turma', 'disciplina', 'modulo', 'prazo_entrega')
    list_filter = ('prazo_entrega', 'turma', 'turma__curso__tipo')
    search_fields = ('titulo', 'turma__nome', 'disciplina__nome', 'modulo__nome')
    autocomplete_fields = ('turma', 'disciplina', 'modulo')
    inlines = (EntregaTrabalhoInline,)


@admin.register(EntregaTrabalho)
class EntregaTrabalhoAdmin(admin.ModelAdmin):
    list_display = ('trabalho', 'aluno', 'data_hora_entrega', 'nota')
    list_filter = ('trabalho__turma',)
    search_fields = ('aluno__user__email', 'aluno__cpf', 'trabalho__titulo')
    readonly_fields = ('data_hora_entrega',)
    autocomplete_fields = ('trabalho', 'aluno')
