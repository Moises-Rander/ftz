"""Serviços do módulo acadêmico (V6).

Regras de acesso reaproveitam as permissões do V2 nas views; aqui ficam as
validações de negócio e as operações em lote (atômicas).
"""
from decimal import Decimal

from django.db import transaction
from django.utils import timezone
from rest_framework.exceptions import PermissionDenied, ValidationError

from cursos.models import AtribuicaoProfessor
from matriculas.models import Matricula

from .models import (
    Avaliacao,
    EntregaTrabalho,
    Frequencia,
    ResultadoAvaliacao,
)


# ---------------------------------------------------------------------------
# Helpers de identidade e atribuição
# ---------------------------------------------------------------------------


def professor_atribuido(professor, turma, disciplina=None, modulo=None):
    """True se o professor está atribuído à turma e à disciplina/módulo do item."""
    filtro = {'professor': professor, 'turma': turma}
    if disciplina is not None:
        filtro['disciplina'] = disciplina
    if modulo is not None:
        filtro['modulo'] = modulo
    return AtribuicaoProfessor.objects.filter(**filtro).exists()


def _exigir_atribuicao(professor, turma, disciplina=None, modulo=None):
    if not professor_atribuido(professor, turma, disciplina, modulo):
        raise PermissionDenied(
            'Você não está atribuído a esta turma/disciplina/módulo.'
        )


def alunos_aprovados_ids(turma):
    """Ids de Aluno com matrícula APROVADA na turma."""
    return set(
        Matricula.objects.filter(
            turma=turma, status=Matricula.Status.APROVADA
        ).values_list('aluno_id', flat=True)
    )


def tem_matricula_aprovada(aluno, turma):
    return Matricula.objects.filter(
        aluno=aluno, turma=turma, status=Matricula.Status.APROVADA
    ).exists()


# ---------------------------------------------------------------------------
# Frequência (lote)
# ---------------------------------------------------------------------------


@transaction.atomic
def lancar_frequencia(*, professor, aula, itens):
    """itens: lista de {'aluno': id, 'presente': bool}. Atômico."""
    if aula.cancelada:
        raise ValidationError('Não é possível lançar frequência para uma aula cancelada.')
    _exigir_atribuicao(professor, aula.turma, aula.disciplina, aula.modulo)

    aprovados = alunos_aprovados_ids(aula.turma)
    # Valida TUDO antes de persistir (atomicidade lógica).
    vistos = set()
    for item in itens:
        aluno_id = item['aluno']
        if aluno_id in vistos:
            raise ValidationError(f'Aluno {aluno_id} repetido na lista.')
        vistos.add(aluno_id)
        if aluno_id not in aprovados:
            raise ValidationError(
                f'Aluno {aluno_id} não possui matrícula aprovada nesta turma.'
            )

    registros = []
    for item in itens:
        freq, _ = Frequencia.objects.update_or_create(
            aula=aula, aluno_id=item['aluno'],
            defaults={'presente': bool(item['presente']), 'lancado_por': professor},
        )
        registros.append(freq)
    return registros


def percentual_presenca(aluno, turma):
    """Percentual de presença do aluno na turma, considerando aulas não canceladas."""
    freqs = Frequencia.objects.filter(
        aluno=aluno, aula__turma=turma, aula__cancelada=False
    )
    total = freqs.count()
    if total == 0:
        return 0.0
    presentes = freqs.filter(presente=True).count()
    return round(presentes * 100 / total, 2)


# ---------------------------------------------------------------------------
# Resultados de avaliação (lote)
# ---------------------------------------------------------------------------


@transaction.atomic
def lancar_resultados(*, professor, avaliacao, itens):
    """itens: lista de {'aluno': id, 'nota': número}. Atômico."""
    _exigir_atribuicao(professor, avaliacao.turma, avaliacao.disciplina, avaliacao.modulo)
    aprovados = alunos_aprovados_ids(avaliacao.turma)

    vistos = set()
    for item in itens:
        aluno_id = item['aluno']
        if aluno_id in vistos:
            raise ValidationError(f'Aluno {aluno_id} repetido na lista.')
        vistos.add(aluno_id)
        if aluno_id not in aprovados:
            raise ValidationError(
                f'Aluno {aluno_id} não possui matrícula aprovada nesta turma.'
            )
        nota = Decimal(str(item['nota']))
        if nota < 0 or nota > avaliacao.nota_maxima:
            raise ValidationError(
                f'Nota {nota} inválida (máximo {avaliacao.nota_maxima}).'
            )

    registros = []
    for item in itens:
        res, _ = ResultadoAvaliacao.objects.update_or_create(
            avaliacao=avaliacao, aluno_id=item['aluno'],
            defaults={'nota': Decimal(str(item['nota'])), 'lancado_por': professor},
        )
        registros.append(res)
    return registros


# ---------------------------------------------------------------------------
# Trabalhos — entrega (aluno) e correção (professor)
# ---------------------------------------------------------------------------


@transaction.atomic
def entregar_trabalho(*, aluno, trabalho, arquivo):
    if not tem_matricula_aprovada(aluno, trabalho.turma):
        raise PermissionDenied('Você não possui matrícula aprovada nesta turma.')

    entrega = EntregaTrabalho.objects.filter(trabalho=trabalho, aluno=aluno).first()
    if entrega and entrega.corrigida:
        raise ValidationError('Este trabalho já foi corrigido; não é possível reenviar.')

    agora = timezone.now()
    atrasada = agora > trabalho.prazo_entrega
    if entrega is None:
        entrega = EntregaTrabalho.objects.create(
            trabalho=trabalho, aluno=aluno, arquivo=arquivo,
            data_hora_entrega=agora, entregue_em_atraso=atrasada,
        )
    else:
        entrega.arquivo = arquivo
        entrega.data_hora_entrega = agora
        entrega.entregue_em_atraso = atrasada
        entrega.save(update_fields=['arquivo', 'data_hora_entrega', 'entregue_em_atraso'])
    return entrega


@transaction.atomic
def corrigir_entrega(*, professor, entrega, nota, feedback=None):
    trabalho = entrega.trabalho
    _exigir_atribuicao(professor, trabalho.turma, trabalho.disciplina, trabalho.modulo)
    if nota is not None:
        nota = Decimal(str(nota))
        if nota < 0:
            raise ValidationError({'nota': 'A nota não pode ser negativa.'})
    entrega.nota = nota
    if feedback is not None:
        entrega.feedback = feedback
    entrega.save(update_fields=['nota', 'feedback'])
    return entrega


# ---------------------------------------------------------------------------
# Boletim consolidado
# ---------------------------------------------------------------------------


def boletim(aluno, turma):
    avaliacoes = Avaliacao.objects.filter(turma=turma).order_by('data')
    resultados = {
        r.avaliacao_id: r for r in ResultadoAvaliacao.objects.filter(
            avaliacao__turma=turma, aluno=aluno
        )
    }
    lista_avaliacoes = []
    soma_obtidas = Decimal('0')
    soma_maximas = Decimal('0')
    for av in avaliacoes:
        res = resultados.get(av.id)
        nota = res.nota if res else None
        lista_avaliacoes.append({
            'avaliacao_id': av.id, 'titulo': av.titulo, 'data': av.data,
            'nota': str(nota) if nota is not None else None,
            'nota_maxima': str(av.nota_maxima),
        })
        if nota is not None:
            soma_obtidas += nota
            soma_maximas += av.nota_maxima

    media_geral = (
        round(float(soma_obtidas * 100 / soma_maximas), 2) if soma_maximas > 0 else None
    )

    from .models import Trabalho
    trabalhos = Trabalho.objects.filter(turma=turma).order_by('prazo_entrega')
    entregas = {
        e.trabalho_id: e for e in EntregaTrabalho.objects.filter(
            trabalho__turma=turma, aluno=aluno
        )
    }
    lista_trabalhos = []
    for tr in trabalhos:
        e = entregas.get(tr.id)
        lista_trabalhos.append({
            'trabalho_id': tr.id, 'titulo': tr.titulo, 'prazo_entrega': tr.prazo_entrega,
            'status': _status_entrega(tr, e),
            'entregue_em_atraso': e.entregue_em_atraso if e else False,
            'nota': str(e.nota) if e and e.nota is not None else None,
            'feedback': e.feedback if e else None,
        })

    return {
        'turma_id': turma.id,
        'percentual_presenca': percentual_presenca(aluno, turma),
        'avaliacoes': lista_avaliacoes,
        'trabalhos': lista_trabalhos,
        'media_geral': media_geral,
    }


def _status_entrega(trabalho, entrega):
    if entrega is None:
        return 'PENDENTE'
    if entrega.corrigida:
        return 'CORRIGIDO'
    return 'ENTREGUE'
