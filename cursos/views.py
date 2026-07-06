from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from accounts.permissions import IsAdmin, IsOwnerAluno

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
from .serializers import (
    AtribuicaoProfessorAdminSerializer,
    CicloAdminSerializer,
    CursoAdminSerializer,
    CursoDetailSerializer,
    CursoListSerializer,
    DisciplinaAdminSerializer,
    GradeCompletaSerializer,
    GradeHorariaAdminSerializer,
    HorarioFormacaoAdminSerializer,
    ModuloAdminSerializer,
    ProfessorAtribuidoSerializer,
    ProgressoModuloTurmaAdminSerializer,
    TurmaAdminSerializer,
    TurmaDetailSerializer,
    TurmaResumoSerializer,
)

# ---------------------------------------------------------------------------
# Público (sem autenticação)
# ---------------------------------------------------------------------------


class CursoPublicViewSet(viewsets.ReadOnlyModelViewSet):
    """Catálogo público de cursos. Lista e detalhe, sem autenticação."""

    permission_classes = (AllowAny,)

    def get_queryset(self):
        qs = Curso.objects.all().prefetch_related('turmas').order_by('nome')
        tipo = self.request.query_params.get('tipo')
        if tipo:
            qs = qs.filter(tipo=tipo.upper())
        busca = self.request.query_params.get('search') or self.request.query_params.get('q')
        if busca:
            qs = qs.filter(nome__icontains=busca)
        return qs

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return CursoDetailSerializer
        return CursoListSerializer

    @action(detail=True, methods=['get'])
    def turmas(self, request, pk=None):
        """Turmas do curso (público: exclui ENCERRADAS)."""
        curso = self.get_object()
        turmas = curso.turmas.exclude(status=Turma.Status.ENCERRADA)
        return Response(TurmaResumoSerializer(turmas, many=True).data)


class TurmaPublicViewSet(viewsets.ReadOnlyModelViewSet):
    """Detalhe público de turma + professores; grade completa restrita."""

    permission_classes = (AllowAny,)
    serializer_class = TurmaDetailSerializer

    def get_queryset(self):
        qs = Turma.objects.select_related('curso')
        # Grade completa é restrita: ali permitimos qualquer turma (checagem de
        # objeto cuida do acesso). Nos demais (público), oculta ENCERRADAS.
        if self.action == 'grade_completa':
            return qs
        return qs.exclude(status=Turma.Status.ENCERRADA)

    @action(detail=True, methods=['get'])
    def professores(self, request, pk=None):
        """Professores atribuídos à turma (público)."""
        turma = self.get_object()
        atribuicoes = (
            AtribuicaoProfessor.objects
            .filter(turma=turma)
            .select_related('professor__user')
        )
        # Remove professores repetidos (várias disciplinas/módulos na mesma turma).
        vistos, unicos = set(), []
        for atr in atribuicoes:
            if atr.professor_id not in vistos:
                vistos.add(atr.professor_id)
                unicos.append(atr)
        return Response(ProfessorAtribuidoSerializer(unicos, many=True).data)

    @action(
        detail=True, methods=['get'], url_path='grade-completa',
        permission_classes=[IsAuthenticated, IsOwnerAluno],
    )
    def grade_completa(self, request, pk=None):
        """Grade horária completa — apenas aluno matriculado (aprovado) ou Admin."""
        turma = self.get_object()  # dispara check_object_permissions (IsOwnerAluno)
        return Response(GradeCompletaSerializer(turma).data)


# ---------------------------------------------------------------------------
# Gerenciamento (somente Admin)
# ---------------------------------------------------------------------------


class CursoAdminViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAdmin,)
    queryset = Curso.objects.all().order_by('nome')
    serializer_class = CursoAdminSerializer


class TurmaAdminViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAdmin,)
    queryset = Turma.objects.select_related('curso').all()
    serializer_class = TurmaAdminSerializer

    @action(detail=True, methods=['post'])
    def fechar(self, request, pk=None):
        """Fecha a turma manualmente (mesmo com vagas disponíveis)."""
        turma = self.get_object()
        if turma.status == Turma.Status.ENCERRADA:
            raise ValidationError('Turma encerrada não pode ser fechada.')
        turma.status = Turma.Status.FECHADA
        turma.save(update_fields=['status'])
        return Response(self.get_serializer(turma).data)

    @action(detail=True, methods=['post'])
    def reabrir(self, request, pk=None):
        """Reabre uma turma FECHADA, desde que as vagas não estejam esgotadas."""
        turma = self.get_object()
        if turma.status != Turma.Status.FECHADA:
            raise ValidationError('Só é possível reabrir turmas FECHADAS.')
        if turma.lotada:
            raise ValidationError('Não é possível reabrir: as vagas estão esgotadas.')
        turma.status = Turma.Status.ABERTA
        turma.save(update_fields=['status'])
        return Response(self.get_serializer(turma).data)


class DisciplinaAdminViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAdmin,)
    queryset = Disciplina.objects.select_related('curso').all()
    serializer_class = DisciplinaAdminSerializer


class CicloAdminViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAdmin,)
    queryset = Ciclo.objects.select_related('turma').all()
    serializer_class = CicloAdminSerializer

    def perform_destroy(self, instance):
        if instance.aulas.exists():
            raise ValidationError(
                'Não é possível excluir um ciclo que possui aulas registradas.'
            )
        instance.delete()

    @action(detail=True, methods=['post'])
    def ativar(self, request, pk=None):
        """Ativa o ciclo, desativando os demais da turma."""
        ciclo = self.get_object()
        ciclo.ativar()
        return Response(self.get_serializer(ciclo).data)


class GradeHorariaAdminViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAdmin,)
    queryset = GradeHoraria.objects.select_related('ciclo', 'disciplina').all()
    serializer_class = GradeHorariaAdminSerializer


class ModuloAdminViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAdmin,)
    queryset = Modulo.objects.select_related('curso').all()
    serializer_class = ModuloAdminSerializer


class ProgressoModuloTurmaAdminViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAdmin,)
    queryset = ProgressoModuloTurma.objects.select_related('turma', 'modulo').all()
    serializer_class = ProgressoModuloTurmaAdminSerializer

    @action(detail=True, methods=['post'])
    def ativar(self, request, pk=None):
        """Ativa este módulo na turma (desativa/conclui o anterior; respeita a ordem)."""
        progresso = self.get_object()
        try:
            progresso.ativar()
        except DjangoValidationError as exc:
            raise ValidationError(exc.messages)
        return Response(self.get_serializer(progresso).data, status=status.HTTP_200_OK)


class HorarioFormacaoAdminViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAdmin,)
    queryset = HorarioFormacao.objects.select_related('turma').all()
    serializer_class = HorarioFormacaoAdminSerializer


class AtribuicaoProfessorAdminViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAdmin,)
    queryset = AtribuicaoProfessor.objects.select_related(
        'professor__user', 'turma', 'disciplina', 'modulo'
    ).all()
    serializer_class = AtribuicaoProfessorAdminSerializer
