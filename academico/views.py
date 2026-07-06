from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.permissions import IsAdmin, IsAluno, IsAtribuidoProfessor, IsOwnerAluno, IsProfessor
from cursos.models import AtribuicaoProfessor, Turma
from matriculas.models import Matricula

from .models import Aula, Avaliacao, EntregaTrabalho, Frequencia, ResultadoAvaliacao, Trabalho
from .serializers import (
    AulaAdminSerializer,
    AulaAlunoSerializer,
    AulaProfessorSerializer,
    AvaliacaoAdminSerializer,
    AvaliacaoAlunoSerializer,
    CorrigirEntregaSerializer,
    EntregaProfessorSerializer,
    EntregaSubmitSerializer,
    FrequenciaLoteSerializer,
    FrequenciaSerializer,
    MinhaEntregaSerializer,
    ResultadoLoteSerializer,
    ResultadoSerializer,
    TrabalhoAdminSerializer,
    TrabalhoAlunoSerializer,
)
from .services import (
    boletim,
    corrigir_entrega,
    entregar_trabalho,
    lancar_frequencia,
    lancar_resultados,
    percentual_presenca,
)


# ---------------------------------------------------------------------------
# Admin — CRUD
# ---------------------------------------------------------------------------


class AulaAdminViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAdmin,)
    queryset = Aula.objects.select_related('turma__curso', 'disciplina', 'modulo', 'ciclo').all()
    serializer_class = AulaAdminSerializer


class AvaliacaoAdminViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAdmin,)
    queryset = Avaliacao.objects.select_related('turma__curso', 'disciplina', 'modulo').all()
    serializer_class = AvaliacaoAdminSerializer


class TrabalhoAdminViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAdmin,)
    queryset = Trabalho.objects.select_related('turma__curso', 'disciplina', 'modulo').all()
    serializer_class = TrabalhoAdminSerializer


# ---------------------------------------------------------------------------
# Professor
# ---------------------------------------------------------------------------

PERM_PROFESSOR = (IsAuthenticated, IsProfessor, IsAtribuidoProfessor)


def _professor(request):
    return request.user.professor


class ProfessorTurmasView(APIView):
    permission_classes = (IsAuthenticated, IsProfessor)

    def get(self, request):
        atribuicoes = (
            AtribuicaoProfessor.objects
            .filter(professor=_professor(request))
            .select_related('turma__curso')
        )
        vistos, turmas = set(), []
        for atr in atribuicoes:
            if atr.turma_id not in vistos:
                vistos.add(atr.turma_id)
                turmas.append({
                    'id': atr.turma.id, 'nome': atr.turma.nome,
                    'curso_nome': atr.turma.curso.nome, 'curso_tipo': atr.turma.curso.tipo,
                    'status': atr.turma.status,
                })
        return Response(turmas)


class ProfessorTurmaAulasView(APIView):
    permission_classes = PERM_PROFESSOR

    def get(self, request, turma_id):
        turma = get_object_or_404(Turma, pk=turma_id)
        self.check_object_permissions(request, turma)
        qs = Aula.objects.filter(turma=turma).select_related('disciplina', 'modulo')
        disciplina = request.query_params.get('disciplina')
        modulo = request.query_params.get('modulo')
        if disciplina:
            qs = qs.filter(disciplina_id=disciplina)
        if modulo:
            qs = qs.filter(modulo_id=modulo)
        return Response(AulaProfessorSerializer(qs.order_by('-data'), many=True).data)


class AulaFrequenciaView(APIView):
    permission_classes = PERM_PROFESSOR

    def _get_aula(self, request, aula_id):
        aula = get_object_or_404(
            Aula.objects.select_related('turma', 'disciplina', 'modulo'), pk=aula_id
        )
        self.check_object_permissions(request, aula)
        return aula

    def get(self, request, aula_id):
        aula = self._get_aula(request, aula_id)
        freqs = Frequencia.objects.filter(aula=aula).select_related('aluno__user')
        return Response(FrequenciaSerializer(freqs, many=True).data)

    def post(self, request, aula_id):
        aula = self._get_aula(request, aula_id)
        serializer = FrequenciaLoteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        registros = lancar_frequencia(
            professor=_professor(request), aula=aula,
            itens=serializer.validated_data['itens'],
        )
        return Response(FrequenciaSerializer(registros, many=True).data,
                        status=status.HTTP_200_OK)


class ProfessorTurmaAlunosView(APIView):
    """Roster de alunos (matrícula APROVADA) de uma turma atribuída — usado nos
    lançamentos de frequência e resultados."""

    permission_classes = PERM_PROFESSOR

    def get(self, request, turma_id):
        turma = get_object_or_404(Turma, pk=turma_id)
        self.check_object_permissions(request, turma)
        matriculas = (
            Matricula.objects
            .filter(turma=turma, status=Matricula.Status.APROVADA)
            .select_related('aluno__user')
            .order_by('aluno__user__first_name', 'aluno__user__email')
        )
        alunos = [
            {'id': m.aluno_id, 'nome': m.aluno.user.get_full_name() or m.aluno.user.email}
            for m in matriculas
        ]
        return Response(alunos)


class AvaliacoesProfessorView(APIView):
    permission_classes = (IsAuthenticated, IsProfessor)

    def get(self, request):
        turma_id = request.query_params.get('turma')
        turmas_ids = AtribuicaoProfessor.objects.filter(
            professor=_professor(request)
        ).values_list('turma_id', flat=True)
        qs = Avaliacao.objects.filter(turma_id__in=list(turmas_ids))
        if turma_id:
            qs = qs.filter(turma_id=turma_id)
        return Response(AvaliacaoAdminSerializer(qs.order_by('-data'), many=True).data)


class TrabalhosProfessorView(APIView):
    """Lista os trabalhos das turmas atribuídas ao professor (filtro por turma)."""

    permission_classes = (IsAuthenticated, IsProfessor)

    def get(self, request):
        turma_id = request.query_params.get('turma')
        turmas_ids = AtribuicaoProfessor.objects.filter(
            professor=_professor(request)
        ).values_list('turma_id', flat=True)
        qs = Trabalho.objects.filter(turma_id__in=list(turmas_ids))
        if turma_id:
            qs = qs.filter(turma_id=turma_id)
        return Response(TrabalhoAdminSerializer(qs.order_by('-prazo_entrega'), many=True).data)


class AvaliacaoResultadosView(APIView):
    permission_classes = PERM_PROFESSOR

    def _get_avaliacao(self, request, avaliacao_id):
        av = get_object_or_404(
            Avaliacao.objects.select_related('turma', 'disciplina', 'modulo'), pk=avaliacao_id
        )
        self.check_object_permissions(request, av)
        return av

    def get(self, request, avaliacao_id):
        av = self._get_avaliacao(request, avaliacao_id)
        res = ResultadoAvaliacao.objects.filter(avaliacao=av).select_related('aluno__user')
        return Response(ResultadoSerializer(res, many=True).data)

    def post(self, request, avaliacao_id):
        av = self._get_avaliacao(request, avaliacao_id)
        serializer = ResultadoLoteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        registros = lancar_resultados(
            professor=_professor(request), avaliacao=av,
            itens=serializer.validated_data['itens'],
        )
        return Response(ResultadoSerializer(registros, many=True).data,
                        status=status.HTTP_200_OK)


class TrabalhoEntregasView(APIView):
    permission_classes = PERM_PROFESSOR

    def get(self, request, trabalho_id):
        trabalho = get_object_or_404(
            Trabalho.objects.select_related('turma', 'disciplina', 'modulo'), pk=trabalho_id
        )
        self.check_object_permissions(request, trabalho)
        entregas = EntregaTrabalho.objects.filter(trabalho=trabalho).select_related('aluno__user')
        return Response(EntregaProfessorSerializer(entregas, many=True).data)


class EntregaCorrigirView(APIView):
    permission_classes = PERM_PROFESSOR

    def patch(self, request, entrega_id):
        entrega = get_object_or_404(
            EntregaTrabalho.objects.select_related('trabalho__turma'), pk=entrega_id
        )
        self.check_object_permissions(request, entrega)
        serializer = CorrigirEntregaSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        entrega = corrigir_entrega(
            professor=_professor(request), entrega=entrega,
            nota=serializer.validated_data.get('nota'),
            feedback=serializer.validated_data.get('feedback'),
        )
        return Response(EntregaProfessorSerializer(entrega).data)


# ---------------------------------------------------------------------------
# Aluno
# ---------------------------------------------------------------------------

PERM_ALUNO = (IsAuthenticated, IsAluno, IsOwnerAluno)


def _aluno(request):
    return request.user.aluno


def _turma_do_aluno(view, request, turma_id):
    turma = get_object_or_404(Turma.objects.select_related('curso'), pk=turma_id)
    view.check_object_permissions(request, turma)  # exige matrícula APROVADA
    return turma


class AlunoTurmaAulasView(APIView):
    permission_classes = PERM_ALUNO

    def get(self, request, turma_id):
        turma = _turma_do_aluno(self, request, turma_id)
        aulas = (
            Aula.objects.filter(turma=turma)
            .select_related('disciplina', 'modulo').order_by('-data')
        )
        return Response(AulaAlunoSerializer(aulas, many=True).data)


class AlunoFrequenciaView(APIView):
    permission_classes = PERM_ALUNO

    def get(self, request, turma_id):
        turma = _turma_do_aluno(self, request, turma_id)
        aluno = _aluno(request)
        freqs = Frequencia.objects.filter(
            aluno=aluno, aula__turma=turma
        ).select_related('aula').order_by('aula__data')
        aulas = [{
            'aula_id': f.aula_id, 'data': f.aula.data,
            'cancelada': f.aula.cancelada, 'presente': f.presente,
        } for f in freqs]
        return Response({
            'turma_id': turma.id,
            'percentual_presenca': percentual_presenca(aluno, turma),
            'aulas': aulas,
        })


class AlunoAvaliacoesView(APIView):
    permission_classes = PERM_ALUNO

    def get(self, request, turma_id):
        turma = _turma_do_aluno(self, request, turma_id)
        aluno = _aluno(request)
        resultados = {
            r.avaliacao_id: r for r in ResultadoAvaliacao.objects.filter(
                avaliacao__turma=turma, aluno=aluno
            )
        }
        avaliacoes = list(Avaliacao.objects.filter(turma=turma).order_by('data'))
        for av in avaliacoes:
            av._resultado_aluno = resultados.get(av.id)
        return Response(AvaliacaoAlunoSerializer(avaliacoes, many=True).data)


class AlunoTrabalhosView(APIView):
    permission_classes = PERM_ALUNO

    def get(self, request, turma_id):
        turma = _turma_do_aluno(self, request, turma_id)
        aluno = _aluno(request)
        entregas = {
            e.trabalho_id: e for e in EntregaTrabalho.objects.filter(
                trabalho__turma=turma, aluno=aluno
            )
        }
        trabalhos = list(Trabalho.objects.filter(turma=turma).order_by('prazo_entrega'))
        for tr in trabalhos:
            tr._entrega_aluno = entregas.get(tr.id)
        return Response(TrabalhoAlunoSerializer(trabalhos, many=True).data)


class AlunoEntregarView(APIView):
    permission_classes = PERM_ALUNO

    def post(self, request, trabalho_id):
        trabalho = get_object_or_404(Trabalho.objects.select_related('turma'), pk=trabalho_id)
        self.check_object_permissions(request, trabalho.turma)
        serializer = EntregaSubmitSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        entrega = entregar_trabalho(
            aluno=_aluno(request), trabalho=trabalho,
            arquivo=serializer.validated_data['arquivo'],
        )
        return Response(MinhaEntregaSerializer(entrega).data, status=status.HTTP_201_CREATED)


class AlunoMinhaEntregaView(APIView):
    permission_classes = PERM_ALUNO

    def get(self, request, trabalho_id):
        trabalho = get_object_or_404(Trabalho.objects.select_related('turma'), pk=trabalho_id)
        self.check_object_permissions(request, trabalho.turma)
        entrega = EntregaTrabalho.objects.filter(trabalho=trabalho, aluno=_aluno(request)).first()
        if entrega is None:
            return Response({'status': 'PENDENTE', 'detail': 'Nenhuma entrega enviada.'})
        return Response(MinhaEntregaSerializer(entrega).data)


class AlunoBoletimView(APIView):
    permission_classes = PERM_ALUNO

    def get(self, request, turma_id):
        turma = _turma_do_aluno(self, request, turma_id)
        return Response(boletim(_aluno(request), turma))
