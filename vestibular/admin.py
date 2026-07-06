from django.contrib import admin

from .models import CandidatoVestibular, EdicaoVestibular
from .services import (
    atualizar_status_candidato,
    notificar_resultado,
    verificar_prazos_expirados,
)


class CandidatoVestibularInline(admin.TabularInline):
    model = CandidatoVestibular
    extra = 0
    fields = ('nome', 'email', 'cpf', 'telefone', 'status', 'notificado_por_email')


@admin.register(EdicaoVestibular)
class EdicaoVestibularAdmin(admin.ModelAdmin):
    list_display = (
        'turma', 'data_prova', 'local_prova', 'prazo_matricula', 'resultado_publicado',
    )
    list_filter = ('resultado_publicado', 'data_prova', 'turma__curso')
    search_fields = ('turma__nome', 'turma__curso__nome', 'local_prova')
    autocomplete_fields = ('turma',)
    inlines = (CandidatoVestibularInline,)
    actions = ('acao_verificar_prazos_expirados',)

    def get_readonly_fields(self, request, obj=None):
        readonly = ['data_criacao']
        # Após publicado, PDF e flag não podem ser alterados.
        if obj is not None and obj.resultado_publicado:
            readonly += ['resultado_pdf', 'resultado_publicado']
        return readonly

    @admin.action(description='Verificar prazos expirados (desistência + lista de espera)')
    def acao_verificar_prazos_expirados(self, request, queryset):
        desistencias, promovidos = verificar_prazos_expirados()
        self.message_user(
            request,
            f'{desistencias} candidato(s) marcados como DESISTIU por prazo expirado; '
            f'{promovidos} promovido(s) da lista de espera.',
        )


@admin.register(CandidatoVestibular)
class CandidatoVestibularAdmin(admin.ModelAdmin):
    list_display = ('nome', 'edicao', 'cpf', 'email', 'status', 'notificado_por_email')
    list_filter = ('status', 'notificado_por_email', 'edicao')
    search_fields = ('nome', 'email', 'cpf')
    actions = ('reenviar_notificacao', 'marcar_desistiu')

    @admin.action(description='Reenviar notificação de resultado (não notificados)')
    def reenviar_notificacao(self, request, queryset):
        enviados, ignorados = 0, 0
        for candidato in queryset.filter(notificado_por_email=False):
            if notificar_resultado(candidato):
                candidato.notificado_por_email = True
                candidato.save(update_fields=['notificado_por_email'])
                enviados += 1
            else:
                ignorados += 1
        self.message_user(
            request,
            f'{enviados} notificação(ões) reenviada(s); {ignorados} sem envio '
            '(status sem notificação ou falha).',
        )

    @admin.action(description='Marcar como DESISTIU (promove lista de espera se aprovado)')
    def marcar_desistiu(self, request, queryset):
        total = 0
        for candidato in queryset:
            atualizar_status_candidato(candidato, CandidatoVestibular.Status.DESISTIU)
            total += 1
        self.message_user(request, f'{total} candidato(s) marcados como DESISTIU.')
