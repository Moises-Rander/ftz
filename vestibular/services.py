"""Serviços do ciclo de vestibular (V5)."""
from django.db import transaction
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from cursos.models import Turma
from notifications.emails import EmailType
from notifications.services import enviar_notificacao

from .models import CandidatoVestibular, EdicaoVestibular

Status = CandidatoVestibular.Status
# Status cujo email de resultado deve ser enviado na publicação/reenvio.
STATUS_COM_NOTIFICACAO_RESULTADO = {Status.APROVADO, Status.REPROVADO, Status.LISTA_ESPERA}


# ---------------------------------------------------------------------------
# Inscrição pública
# ---------------------------------------------------------------------------


@transaction.atomic
def inscrever_candidato(*, edicao, nome, email, cpf, telefone=''):
    if edicao.turma.status != Turma.Status.ABERTA:
        raise ValidationError('As inscrições para esta edição não estão abertas.')
    if CandidatoVestibular.objects.filter(edicao=edicao, cpf=cpf).exists():
        raise ValidationError({'cpf': 'Já existe uma inscrição com este CPF nesta edição.'})

    candidato = CandidatoVestibular.objects.create(
        edicao=edicao, nome=nome, email=email, cpf=cpf, telefone=telefone,
        status=Status.INSCRITO, notificado_por_email=False,
    )
    _email_confirmacao_inscricao(candidato)
    return candidato


# ---------------------------------------------------------------------------
# Gestão de status / lista de espera
# ---------------------------------------------------------------------------


def promover_lista_espera(edicao):
    """Promove o primeiro candidato em LISTA_ESPERA (menor id) para APROVADO.

    Retorna o candidato promovido ou None se a lista estiver vazia.
    """
    proximo = (
        CandidatoVestibular.objects
        .filter(edicao=edicao, status=Status.LISTA_ESPERA)
        .order_by('id')
        .first()
    )
    if proximo is None:
        return None
    proximo.status = Status.APROVADO
    proximo.notificado_por_email = False
    proximo.save(update_fields=['status', 'notificado_por_email'])
    # Notifica imediatamente sobre a promoção (independe de publicação).
    if _notificar_promocao(proximo):
        proximo.notificado_por_email = True
        proximo.save(update_fields=['notificado_por_email'])
    return proximo


@transaction.atomic
def atualizar_status_candidato(candidato, novo_status):
    """Aplica a mudança de status com as regras de negócio associadas."""
    if novo_status not in Status.values:
        raise ValidationError({'status': 'Status inválido.'})

    status_anterior = candidato.status

    # DESISTIU de um APROVADO dispara a promoção da lista de espera.
    if novo_status == Status.DESISTIU:
        candidato.status = Status.DESISTIU
        candidato.save(update_fields=['status'])
        if status_anterior == Status.APROVADO:
            promover_lista_espera(candidato.edicao)
        return candidato

    # Mudança para resultado ainda não comunicado: reseta a notificação.
    if novo_status in STATUS_COM_NOTIFICACAO_RESULTADO:
        candidato.notificado_por_email = False
    candidato.status = novo_status
    candidato.save(update_fields=['status', 'notificado_por_email'])
    return candidato


# ---------------------------------------------------------------------------
# Publicação de resultado e notificações
# ---------------------------------------------------------------------------


def notificar_resultado(candidato):
    """Envia o email de resultado conforme o status. Retorna True em sucesso.

    O serviço central já é tolerante a falhas (loga e retorna False sem levantar).
    """
    if candidato.status == Status.APROVADO:
        return _email_aprovado(candidato)
    if candidato.status == Status.REPROVADO:
        return _email_reprovado(candidato)
    if candidato.status == Status.LISTA_ESPERA:
        return _email_lista_espera(candidato)
    return False


def notificar_pendentes(edicao):
    """Notifica candidatos ainda não notificados; marca sucesso e conta falhas.

    Tolerante a falhas: um email que falhe não interrompe os demais e o
    candidato permanece com notificado_por_email=False para reenvio.
    """
    pendentes = edicao.candidatos.filter(
        notificado_por_email=False, status__in=STATUS_COM_NOTIFICACAO_RESULTADO
    ).order_by('id')
    enviados, falhas = 0, 0
    for candidato in pendentes:
        if notificar_resultado(candidato):
            candidato.notificado_por_email = True
            candidato.save(update_fields=['notificado_por_email'])
            enviados += 1
        else:
            falhas += 1
    return enviados, falhas


def publicar_resultado(edicao, pdf):
    """Anexa o PDF, publica o resultado e notifica os candidatos pendentes.

    Após publicado, PDF e flag não podem ser alterados.
    """
    if edicao.resultado_publicado:
        raise ValidationError('O resultado desta edição já foi publicado.')
    edicao.resultado_pdf = pdf
    edicao.resultado_publicado = True
    edicao.save(update_fields=['resultado_pdf', 'resultado_publicado'])
    enviados, falhas = notificar_pendentes(edicao)
    return enviados, falhas


# ---------------------------------------------------------------------------
# Verificação de prazos expirados
# ---------------------------------------------------------------------------


def verificar_prazos_expirados():
    """Marca como DESISTIU aprovados fora do prazo sem matrícula aprovada e
    promove a lista de espera. Retorna quantos desistiram e quantos foram promovidos."""
    from matriculas.models import Matricula

    hoje = timezone.localdate()
    desistencias, promovidos = 0, 0
    edicoes = EdicaoVestibular.objects.filter(resultado_publicado=True)
    for edicao in edicoes:
        if edicao.prazo_matricula >= hoje:
            continue
        # Snapshot dos aprovados antes de promover novos da lista de espera.
        aprovados = list(edicao.candidatos.filter(status=Status.APROVADO))
        for candidato in aprovados:
            tem_matricula = Matricula.objects.filter(
                turma=edicao.turma, candidato_cpf=candidato.cpf,
                status=Matricula.Status.APROVADA,
            ).exists()
            if tem_matricula:
                continue
            # DESISTIU + promoção da lista de espera (uma única promoção por vaga).
            candidato.status = Status.DESISTIU
            candidato.save(update_fields=['status'])
            desistencias += 1
            if promover_lista_espera(edicao) is not None:
                promovidos += 1
    return desistencias, promovidos


# ---------------------------------------------------------------------------
# Emails
# ---------------------------------------------------------------------------


def _email_confirmacao_inscricao(candidato):
    ed = candidato.edicao
    return enviar_notificacao(
        EmailType.VESTIBULAR_INSCRICAO_CONFIRMADA, candidato.email, {
            'nome': candidato.nome,
            'turma': str(ed.turma),
            'data_prova': f'{ed.data_prova:%d/%m/%Y}',
            'local_prova': ed.local_prova,
        })


def _email_aprovado(candidato):
    ed = candidato.edicao
    return enviar_notificacao(
        EmailType.VESTIBULAR_RESULTADO_APROVADO, candidato.email, {
            'nome': candidato.nome,
            'turma': str(ed.turma),
            'prazo': f'{ed.prazo_matricula:%d/%m/%Y}',
        })


def _email_reprovado(candidato):
    return enviar_notificacao(
        EmailType.VESTIBULAR_RESULTADO_REPROVADO, candidato.email, {
            'nome': candidato.nome,
            'turma': str(candidato.edicao.turma),
        })


def _email_lista_espera(candidato):
    ed = candidato.edicao
    posicao = CandidatoVestibular.objects.filter(
        edicao=ed, status=Status.LISTA_ESPERA, id__lte=candidato.id
    ).count()
    return enviar_notificacao(
        EmailType.VESTIBULAR_RESULTADO_LISTA_ESPERA, candidato.email, {
            'nome': candidato.nome,
            'turma': str(ed.turma),
            'posicao': posicao,
        })


def _notificar_promocao(candidato):
    ed = candidato.edicao
    return enviar_notificacao(
        EmailType.VESTIBULAR_PROMOVIDO_LISTA_ESPERA, candidato.email, {
            'nome': candidato.nome,
            'turma': str(ed.turma),
            'prazo': f'{ed.prazo_matricula:%d/%m/%Y}',
        })
