from django.contrib import admin
from django.core.exceptions import ValidationError
from django.utils.html import format_html

from .models import Cupom, Documento, Matricula, Promocao
from .services import aprovar_matricula, rejeitar_matricula


class DocumentoInline(admin.TabularInline):
    model = Documento
    extra = 0
    fields = ('tipo', 'arquivo', 'preview', 'status')
    readonly_fields = ('preview',)

    @admin.display(description='visualizar/baixar')
    def preview(self, obj):
        if obj and obj.arquivo:
            return format_html('<a href="{}" target="_blank">abrir arquivo</a>', obj.arquivo.url)
        return '—'


@admin.register(Matricula)
class MatriculaAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'candidato_nome', 'turma', 'status', 'metodo_pagamento',
        'valor_final', 'pagamento_asaas', 'data_criacao',
    )
    list_display_links = ('id', 'candidato_nome')
    list_filter = ('status', 'metodo_pagamento', 'turma__curso', 'turma')
    search_fields = (
        'candidato_nome', 'candidato_email', 'candidato_cpf',
        'aluno__user__email', 'turma__nome', 'asaas_payment_id',
    )
    readonly_fields = (
        'data_criacao', 'resumo_financeiro', 'pagamento_asaas', 'upload_token',
    )
    autocomplete_fields = ('aluno', 'turma', 'cupom', 'promocao')
    inlines = (DocumentoInline,)
    actions = ('aprovar_matriculas', 'rejeitar_matriculas')
    fieldsets = (
        ('Candidato', {
            'fields': (
                'candidato_nome', 'candidato_email', 'candidato_cpf',
                'candidato_telefone', 'candidato_data_nascimento',
            ),
        }),
        ('Matrícula', {'fields': ('turma', 'status', 'motivo_rejeicao', 'aluno')}),
        ('Financeiro', {
            'fields': (
                'metodo_pagamento', 'valor_original', 'desconto_cupom',
                'desconto_promocao', 'valor_final', 'resumo_financeiro',
                'cupom', 'promocao',
            ),
        }),
        ('Pagamento (Asaas)', {
            'fields': ('asaas_payment_id', 'url_pagamento', 'pagamento_asaas'),
        }),
        ('Metadados', {'fields': ('upload_token', 'data_criacao')}),
    )

    @admin.display(description='Resumo do valor')
    def resumo_financeiro(self, obj):
        return format_html(
            'Original: <b>R$ {}</b> — Promoção: −R$ {} — Cupom: −R$ {} '
            '⇒ Final: <b>R$ {}</b>',
            obj.valor_original, obj.desconto_promocao, obj.desconto_cupom, obj.valor_final,
        )

    @admin.display(description='Pagamento Asaas')
    def pagamento_asaas(self, obj):
        if obj.valor_final == 0:
            return 'Isento (sem cobrança)'
        if not obj.asaas_payment_id:
            return 'Sem cobrança gerada'
        confirmado = obj.status in (
            Matricula.Status.AGUARDANDO_VALIDACAO, Matricula.Status.APROVADA
        )
        rotulo = 'Confirmado' if confirmado else 'Aguardando'
        if obj.url_pagamento:
            return format_html(
                '{} — <a href="{}" target="_blank">{}</a>',
                rotulo, obj.url_pagamento, obj.asaas_payment_id,
            )
        return f'{rotulo} — {obj.asaas_payment_id}'

    @admin.action(description='Aprovar matrículas selecionadas')
    def aprovar_matriculas(self, request, queryset):
        aprovadas = 0
        for matricula in queryset.exclude(status=Matricula.Status.APROVADA):
            try:
                aprovar_matricula(matricula)
                aprovadas += 1
            except ValidationError as exc:
                self.message_user(
                    request, f'#{matricula.id}: {exc.messages[0]}', level='warning'
                )
        if aprovadas:
            self.message_user(
                request,
                f'{aprovadas} matrícula(s) aprovada(s). Contas de aluno criadas e '
                'email de definição de senha enviado.',
            )

    @admin.action(description='Rejeitar matrículas selecionadas')
    def rejeitar_matriculas(self, request, queryset):
        atualizadas = 0
        for matricula in queryset.exclude(status=Matricula.Status.REJEITADA):
            motivo = matricula.motivo_rejeicao or 'Rejeitada pelo administrador.'
            rejeitar_matricula(matricula, motivo)
            atualizadas += 1
        if atualizadas:
            self.message_user(
                request,
                f'{atualizadas} matrícula(s) rejeitada(s); candidato(s) notificado(s) por email. '
                'Para um motivo específico, preencha-o na matrícula antes de rejeitar.',
            )


@admin.register(Documento)
class DocumentoAdmin(admin.ModelAdmin):
    list_display = ('matricula', 'tipo', 'status')
    list_filter = ('tipo', 'status')
    search_fields = ('matricula__candidato_cpf', 'matricula__candidato_email')
    autocomplete_fields = ('matricula',)


@admin.register(Cupom)
class CupomAdmin(admin.ModelAdmin):
    list_display = (
        'codigo', 'tipo_desconto', 'valor_desconto', 'data_inicio', 'data_fim',
        'usos_atuais', 'max_usos', 'is_ativo',
    )
    list_filter = ('tipo_desconto', 'is_ativo', 'curso')
    search_fields = ('codigo',)
    readonly_fields = ('usos_atuais',)
    autocomplete_fields = ('curso',)


@admin.register(Promocao)
class PromocaoAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'tipo_desconto', 'valor', 'data_inicio', 'data_fim', 'is_ativa')
    list_filter = ('tipo_desconto', 'is_ativa', 'curso', 'turma')
    search_fields = ('curso__nome', 'turma__nome')
    autocomplete_fields = ('turma', 'curso')
