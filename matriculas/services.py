"""Serviços do fluxo de matrícula e pagamento (V4)."""
from decimal import Decimal

from django.conf import settings
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import transaction
from django.db.models import F, Q
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from accounts.services import criar_usuario_aluno, enviar_email_senha
from cursos.models import Turma
from notifications.emails import EmailType
from notifications.services import enviar_notificacao, enviar_para_admin
from vestibular.models import CandidatoVestibular

from .asaas import get_asaas_client
from .models import Cupom, Documento, Matricula, Promocao

ZERO = Decimal('0.00')


# ---------------------------------------------------------------------------
# Cálculo de descontos
# ---------------------------------------------------------------------------


def buscar_promocao_vigente(turma, em=None):
    """Promoção ativa e vigente para a turma (preferencial) ou curso."""
    hoje = em or timezone.localdate()
    qs = Promocao.objects.filter(
        is_ativa=True, data_inicio__lte=hoje, data_fim__gte=hoje
    ).filter(Q(turma=turma) | Q(curso=turma.curso))
    # Prioriza promoção específica da turma.
    return qs.filter(turma=turma).first() or qs.filter(curso=turma.curso).first()


def calcular_valores(turma, cupom=None, em=None):
    """Retorna (valor_original, desconto_promo, desconto_cupom, valor_final, promocao)."""
    valor_original = Decimal(turma.curso.preco_base)
    promocao = buscar_promocao_vigente(turma, em=em)
    desconto_promo = promocao.calcular_desconto(valor_original) if promocao else ZERO
    desconto_cupom = cupom.calcular_desconto(valor_original) if cupom else ZERO
    valor_final = valor_original - desconto_promo - desconto_cupom
    if valor_final < ZERO:
        valor_final = ZERO
    return valor_original, desconto_promo, desconto_cupom, valor_final, promocao


# ---------------------------------------------------------------------------
# Etapa 1 + 2 — iniciar matrícula e gerar pagamento
# ---------------------------------------------------------------------------


def _validar_pre_requisitos(*, turma, cpf):
    if turma.status != Turma.Status.ABERTA:
        raise ValidationError('Esta turma não está aberta para matrículas.')

    ja_aprovada = Matricula.objects.filter(
        turma=turma, candidato_cpf=cpf, status=Matricula.Status.APROVADA
    ).exists()
    if ja_aprovada:
        raise ValidationError('Já existe uma matrícula aprovada para este CPF nesta turma.')

    # Pré-requisitos específicos de Graduação: aprovação no vestibular + prazo.
    if turma.curso.is_graduacao:
        candidato = CandidatoVestibular.objects.filter(
            edicao__turma=turma, cpf=cpf,
            status=CandidatoVestibular.Status.APROVADO,
        ).select_related('edicao').first()
        if candidato is None:
            raise ValidationError(
                'É necessário ter sido aprovado no vestibular desta turma para se matricular.'
            )
        if candidato.edicao.prazo_matricula < timezone.localdate():
            raise ValidationError(
                'O prazo de matrícula após a aprovação no vestibular está encerrado.'
            )


def _resolver_cupom(codigo, turma):
    if not codigo:
        return None
    cupom = Cupom.objects.filter(codigo=codigo).first()
    if cupom is None or not cupom.esta_valido(curso=turma.curso):
        raise ValidationError({'codigo_cupom': 'Cupom inválido, expirado ou esgotado.'})
    return cupom


@transaction.atomic
def iniciar_matricula(*, turma, nome, email, cpf, telefone='', data_nascimento=None,
                      metodo_pagamento, codigo_cupom=''):
    """Valida, calcula valores, cria a Matrícula e gera o pagamento no Asaas.

    Retorna ``(matricula, pagamento_info)``. Para valor final zero, pula o
    Asaas e avança direto para AGUARDANDO_VALIDACAO.
    """
    _validar_pre_requisitos(turma=turma, cpf=cpf)
    cupom = _resolver_cupom(codigo_cupom, turma)

    valor_original, desc_promo, desc_cupom, valor_final, promocao = calcular_valores(turma, cupom)

    matricula = Matricula.objects.create(
        turma=turma,
        candidato_nome=nome,
        candidato_email=email,
        candidato_cpf=cpf,
        candidato_telefone=telefone,
        candidato_data_nascimento=data_nascimento,
        status=Matricula.Status.AGUARDANDO_PAGAMENTO,
        metodo_pagamento=metodo_pagamento,
        valor_original=valor_original,
        desconto_promocao=desc_promo,
        desconto_cupom=desc_cupom,
        valor_final=valor_final,
        cupom=cupom,
        promocao=promocao,
    )

    if cupom is not None:
        Cupom.objects.filter(pk=cupom.pk).update(usos_atuais=F('usos_atuais') + 1)

    # Valor zero: sem cobrança no Asaas; vai direto para validação.
    if valor_final == ZERO:
        matricula.status = Matricula.Status.AGUARDANDO_VALIDACAO
        matricula.save(update_fields=['status'])
        _email_documentos_e_admin(matricula)
        return matricula, {
            'matricula_id': matricula.id,
            'valor_final': str(valor_final),
            'pagamento_necessario': False,
            'upload_token': matricula.upload_token,
            'upload_url': _upload_url(matricula),
        }

    # Cria/recupera cliente e cobrança no Asaas.
    client = get_asaas_client()
    customer_id = client.criar_ou_recuperar_cliente(
        nome=nome, cpf=cpf, email=email, telefone=telefone
    )
    pagamento = client.criar_cobranca(
        customer_id=customer_id, valor=valor_final, metodo=metodo_pagamento,
        descricao=f'Matrícula {turma}', referencia=str(matricula.id),
    )

    matricula.asaas_payment_id = pagamento['asaas_payment_id']
    matricula.url_pagamento = pagamento.get('url_pagamento', '')
    matricula.save(update_fields=['asaas_payment_id', 'url_pagamento'])

    _email_inicio_processo(matricula, pagamento)

    pagamento_info = {
        'matricula_id': matricula.id,
        'valor_final': str(valor_final),
        'pagamento_necessario': True,
        'metodo_pagamento': metodo_pagamento,
        'upload_token': matricula.upload_token,
        'upload_url': _upload_url(matricula),
        **{k: v for k, v in pagamento.items() if k != 'asaas_payment_id'},
    }
    return matricula, pagamento_info


# ---------------------------------------------------------------------------
# Etapa 3 — confirmação do pagamento via webhook (idempotente)
# ---------------------------------------------------------------------------

# Eventos do Asaas que representam pagamento efetivado.
EVENTOS_PAGAMENTO_CONFIRMADO = {'PAYMENT_CONFIRMED', 'PAYMENT_RECEIVED'}


def webhook_autentico(headers):
    """Verifica o token enviado pelo Asaas no header do webhook.

    Usa comparação de tempo constante (evita timing attack).
    """
    import hmac
    token = headers.get('asaas-access-token') or headers.get('Asaas-Access-Token')
    if not token or not settings.ASAAS_WEBHOOK_TOKEN:
        return False
    return hmac.compare_digest(str(token), str(settings.ASAAS_WEBHOOK_TOKEN))


@transaction.atomic
def processar_webhook(payload):
    """Processa o evento do Asaas de forma idempotente.

    Só promove AGUARDANDO_PAGAMENTO -> AGUARDANDO_VALIDACAO uma única vez.
    Retorna um pequeno dict de status para o corpo da resposta.
    """
    evento = (payload or {}).get('event')
    pagamento = (payload or {}).get('payment') or {}
    payment_id = pagamento.get('id')

    if evento not in EVENTOS_PAGAMENTO_CONFIRMADO or not payment_id:
        return {'ignored': True}

    matricula = (
        Matricula.objects.select_for_update()
        .filter(asaas_payment_id=payment_id).first()
    )
    if matricula is None:
        return {'ignored': True, 'reason': 'matricula_nao_encontrada'}

    # Idempotência: só age quando ainda está aguardando pagamento.
    if matricula.status != Matricula.Status.AGUARDANDO_PAGAMENTO:
        return {'ignored': True, 'reason': 'ja_processado'}

    matricula.status = Matricula.Status.AGUARDANDO_VALIDACAO
    matricula.save(update_fields=['status'])
    _email_pagamento_confirmado(matricula)
    _email_documentos_e_admin(matricula, somente_admin=True)
    return {'processed': True, 'matricula_id': matricula.id}


# ---------------------------------------------------------------------------
# Etapa 4 — upload de documentos via token
# ---------------------------------------------------------------------------


def matricula_por_token(token):
    if not token:
        return None
    return Matricula.objects.filter(upload_token=token).first()


def registrar_documentos(token, arquivos):
    """Recebe {tipo: arquivo} e associa à matrícula do token.

    Exige token válido e matrícula em AGUARDANDO_VALIDACAO. Substitui um
    documento já enviado do mesmo tipo.
    """
    matricula = matricula_por_token(token)
    if matricula is None:
        raise ValidationError({'token': 'Token de upload inválido.'})
    if not matricula.token_valido:
        raise ValidationError({'token': 'Este token expirou (matrícula já encerrada).'})
    if matricula.status != Matricula.Status.AGUARDANDO_VALIDACAO:
        raise ValidationError(
            'Os documentos só podem ser enviados após a confirmação do pagamento.'
        )

    exigidos = set(matricula.documentos_exigidos)
    criados = []
    for tipo, arquivo in arquivos.items():
        if tipo not in exigidos:
            raise ValidationError(
                {tipo: 'Tipo de documento não exigido para esta matrícula.'}
            )
        doc, _ = Documento.objects.update_or_create(
            matricula=matricula, tipo=tipo,
            defaults={'arquivo': arquivo, 'status': Documento.Status.PENDENTE},
        )
        criados.append(doc)
    return matricula, criados


# ---------------------------------------------------------------------------
# Etapa 5 — aprovação / rejeição pelo Admin
# ---------------------------------------------------------------------------


@transaction.atomic
def aprovar_matricula(matricula):
    """Aprova a matrícula: revalida vaga, cria a conta do aluno e vincula.

    Levanta ``DjangoValidationError`` se não houver mais vaga (Admin é avisado).
    """
    turma = Turma.objects.select_for_update().get(pk=matricula.turma_id)
    ocupadas = Matricula.objects.filter(
        turma=turma, status=Matricula.Status.APROVADA
    ).exclude(pk=matricula.pk).count()
    if ocupadas >= turma.vagas_totais:
        raise DjangoValidationError(
            'Não há mais vagas nesta turma — aprovação bloqueada.'
        )

    # 1) email de aprovação; 2) criação da conta dispara o "defina sua senha".
    _email_aprovada(matricula)
    aluno = criar_usuario_aluno(
        email=matricula.candidato_email,
        cpf=matricula.candidato_cpf,
        first_name=_primeiro_nome(matricula.candidato_nome),
        last_name=_sobrenome(matricula.candidato_nome),
        telefone=matricula.candidato_telefone,
        data_nascimento=matricula.candidato_data_nascimento,
        enviar_email=True,  # dispara CONTA_DEFINIR_SENHA
    )

    matricula.aluno = aluno
    matricula.status = Matricula.Status.APROVADA
    matricula.motivo_rejeicao = ''
    matricula.save(update_fields=['aluno', 'status', 'motivo_rejeicao'])
    turma.sincronizar_status_vagas()
    return aluno


@transaction.atomic
def rejeitar_matricula(matricula, motivo):
    if not motivo:
        raise DjangoValidationError('Informe o motivo da rejeição.')
    matricula.status = Matricula.Status.REJEITADA
    matricula.motivo_rejeicao = motivo
    matricula.save(update_fields=['status', 'motivo_rejeicao'])
    _email_rejeicao(matricula)


# ---------------------------------------------------------------------------
# Helpers de email / utilitários
# ---------------------------------------------------------------------------


def _upload_url(matricula):
    base = settings.FRONTEND_URL.rstrip('/')
    return f'{base}/matricula/documentos?token={matricula.upload_token}'


def _admin_url(matricula):
    base = settings.BACKEND_URL.rstrip('/')
    return f'{base}/admin/matriculas/matricula/{matricula.id}/change/'


def _primeiro_nome(nome):
    return (nome or '').split(' ', 1)[0]


def _sobrenome(nome):
    partes = (nome or '').split(' ', 1)
    return partes[1] if len(partes) > 1 else ''


def _email_inicio_processo(matricula, pagamento):
    enviar_notificacao(EmailType.MATRICULA_INICIADA, matricula.candidato_email, {
        'nome': matricula.candidato_nome,
        'curso': matricula.turma.curso.nome,
        'turma': str(matricula.turma),
        'valor': matricula.valor_final,
        'metodo': matricula.get_metodo_pagamento_display(),
        'pix_copia_cola': pagamento.get('pix_copia_cola'),
        'boleto_linha': pagamento.get('boleto_linha_digitavel'),
        'url_pagamento': pagamento.get('url_pagamento'),
    })


def _email_pagamento_confirmado(matricula):
    enviar_notificacao(
        EmailType.MATRICULA_PAGAMENTO_CONFIRMADO, matricula.candidato_email, {
            'nome': matricula.candidato_nome,
            'upload_url': _upload_url(matricula),
            'documentos': [str(t) for t in matricula.documentos_exigidos],
            'isento': False,
        })


def _email_documentos_e_admin(matricula, somente_admin=False):
    # Fluxo de valor zero: informa o candidato (isento) e notifica o Admin.
    if not somente_admin:
        enviar_notificacao(
            EmailType.MATRICULA_PAGAMENTO_CONFIRMADO, matricula.candidato_email, {
                'nome': matricula.candidato_nome,
                'upload_url': _upload_url(matricula),
                'documentos': [str(t) for t in matricula.documentos_exigidos],
                'isento': True,
            })
    enviar_para_admin(EmailType.MATRICULA_AGUARDANDO_VALIDACAO, {
        'candidato_nome': matricula.candidato_nome,
        'curso': matricula.turma.curso.nome,
        'turma': str(matricula.turma),
        'admin_url': _admin_url(matricula),
    })


def _email_aprovada(matricula):
    enviar_notificacao(EmailType.MATRICULA_APROVADA, matricula.candidato_email, {
        'nome': matricula.candidato_nome,
        'curso': matricula.turma.curso.nome,
        'turma': str(matricula.turma),
    })


def _email_rejeicao(matricula):
    enviar_notificacao(EmailType.MATRICULA_REJEITADA, matricula.candidato_email, {
        'nome': matricula.candidato_nome,
        'turma': str(matricula.turma),
        'motivo': matricula.motivo_rejeicao,
    })
