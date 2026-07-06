from django.contrib import admin

from .models import (
    AtribuicaoProfessor,
    Ciclo,
    Curso,
    Disciplina,
    GradeHoraria,
    HorarioFormacao,
    Modulo,
    ProgressoModuloTurma,
    Turma,
)


class AtribuicaoProfessorInline(admin.TabularInline):
    model = AtribuicaoProfessor
    extra = 1
    autocomplete_fields = ('professor', 'disciplina', 'modulo')


class ProgressoModuloTurmaInline(admin.TabularInline):
    model = ProgressoModuloTurma
    extra = 0
    autocomplete_fields = ('modulo',)


@admin.register(Curso)
class CursoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'tipo', 'carga_horaria', 'preco_base')
    list_filter = ('tipo',)
    search_fields = ('nome', 'descricao')


@admin.register(Turma)
class TurmaAdmin(admin.ModelAdmin):
    list_display = (
        'curso', 'nome', 'status', 'vagas_totais', 'vagas_ocupadas', 'vagas_disponiveis',
    )
    list_filter = ('status', 'curso__tipo', 'curso')
    search_fields = ('nome', 'curso__nome')
    readonly_fields = ('vagas_ocupadas', 'vagas_disponiveis')
    autocomplete_fields = ('curso',)
    inlines = (AtribuicaoProfessorInline, ProgressoModuloTurmaInline)


@admin.register(Disciplina)
class DisciplinaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'curso')
    list_filter = ('curso',)
    search_fields = ('nome', 'descricao', 'ementa')
    autocomplete_fields = ('curso',)


class GradeHorariaInline(admin.TabularInline):
    model = GradeHoraria
    extra = 1
    autocomplete_fields = ('disciplina',)


@admin.register(Ciclo)
class CicloAdmin(admin.ModelAdmin):
    list_display = ('turma', 'numero', 'data_inicio', 'data_fim', 'is_ativo')
    list_filter = ('is_ativo', 'turma')
    search_fields = ('turma__nome', 'turma__curso__nome')
    list_editable = ('is_ativo',)
    autocomplete_fields = ('turma',)
    inlines = (GradeHorariaInline,)
    actions = ('ativar_ciclos', 'desativar_ciclos')

    @admin.action(description='Ativar ciclo selecionado (1 por turma)')
    def ativar_ciclos(self, request, queryset):
        ativados = 0
        for ciclo in queryset:
            if Ciclo.objects.filter(turma=ciclo.turma, is_ativo=True).exclude(pk=ciclo.pk).exists():
                self.message_user(
                    request,
                    f'{ciclo}: já há um ciclo ativo nesta turma — ignorado.',
                    level='warning',
                )
                continue
            ciclo.is_ativo = True
            ciclo.save(update_fields=['is_ativo'])
            ativados += 1
        if ativados:
            self.message_user(request, f'{ativados} ciclo(s) ativado(s).')

    @admin.action(description='Desativar ciclos selecionados')
    def desativar_ciclos(self, request, queryset):
        atualizados = queryset.update(is_ativo=False)
        self.message_user(request, f'{atualizados} ciclo(s) desativado(s).')


@admin.register(GradeHoraria)
class GradeHorariaAdmin(admin.ModelAdmin):
    list_display = ('ciclo', 'disciplina', 'dia_semana', 'horario', 'slots')
    list_filter = ('dia_semana', 'ciclo__turma')
    search_fields = ('disciplina__nome', 'ciclo__turma__nome')
    autocomplete_fields = ('ciclo', 'disciplina')


@admin.register(Modulo)
class ModuloAdmin(admin.ModelAdmin):
    list_display = ('nome', 'curso', 'ordem')
    list_filter = ('curso',)
    search_fields = ('nome', 'descricao', 'curso__nome')
    autocomplete_fields = ('curso',)


@admin.register(ProgressoModuloTurma)
class ProgressoModuloTurmaAdmin(admin.ModelAdmin):
    list_display = ('turma', 'modulo', 'status', 'is_ativo')
    list_filter = ('status', 'is_ativo', 'turma')
    search_fields = ('turma__nome', 'modulo__nome', 'turma__curso__nome')
    list_editable = ('status', 'is_ativo')
    autocomplete_fields = ('turma', 'modulo')
    actions = ('ativar_modulos', 'concluir_modulos')

    @admin.action(description='Ativar módulo selecionado na turma (1 por turma)')
    def ativar_modulos(self, request, queryset):
        ativados = 0
        for progresso in queryset:
            if ProgressoModuloTurma.objects.filter(
                turma=progresso.turma, is_ativo=True
            ).exclude(pk=progresso.pk).exists():
                self.message_user(
                    request,
                    f'{progresso}: já há um módulo ativo nesta turma — ignorado.',
                    level='warning',
                )
                continue
            progresso.status = ProgressoModuloTurma.Status.ATIVO
            progresso.is_ativo = True
            progresso.save(update_fields=['status', 'is_ativo'])
            ativados += 1
        if ativados:
            self.message_user(request, f'{ativados} módulo(s) ativado(s) na turma.')

    @admin.action(description='Concluir módulos selecionados')
    def concluir_modulos(self, request, queryset):
        atualizados = queryset.update(
            status=ProgressoModuloTurma.Status.CONCLUIDO, is_ativo=False
        )
        self.message_user(request, f'{atualizados} módulo(s) concluído(s).')


@admin.register(HorarioFormacao)
class HorarioFormacaoAdmin(admin.ModelAdmin):
    list_display = ('turma', 'dia_1', 'dia_2', 'horario_inicio', 'duracao_minutos')
    list_filter = ('dia_1', 'dia_2', 'turma')
    search_fields = ('turma__nome', 'turma__curso__nome')
    autocomplete_fields = ('turma',)


@admin.register(AtribuicaoProfessor)
class AtribuicaoProfessorAdmin(admin.ModelAdmin):
    list_display = ('professor', 'turma', 'disciplina', 'modulo')
    list_filter = ('turma', 'turma__curso__tipo')
    search_fields = (
        'professor__user__first_name', 'professor__user__last_name',
        'professor__user__email', 'turma__nome',
    )
    autocomplete_fields = ('professor', 'turma', 'disciplina', 'modulo')
