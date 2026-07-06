from django.http import FileResponse
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.exceptions import NotFound, PermissionDenied
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.models import User
from accounts.permissions import IsAdmin, IsAluno, IsOwnerAluno

from .models import Documento, Matricula
from .serializers import (
    DocumentoSerializer,
    MatriculaAdminSerializer,
    MatriculaAlunoDetailSerializer,
    MatriculaAlunoListSerializer,
    MatriculaCreateSerializer,
    MatriculaStatusSerializer,
)
from .services import (
    iniciar_matricula,
    matricula_por_token,
    processar_webhook,
    registrar_documentos,
    webhook_autentico,
)


class MatriculasView(APIView):
    """POST público (inicia matrícula) e GET do aluno (lista as próprias)."""

    def get_permissions(self):
        if self.request.method == 'POST':
            return [AllowAny()]
        return [IsAuthenticated(), IsAluno()]

    def post(self, request):
        serializer = MatriculaCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        _matricula, info = iniciar_matricula(**serializer.validated_data)
        return Response(info, status=status.HTTP_201_CREATED)

    def get(self, request):
        qs = (
            Matricula.objects
            .filter(aluno__user=request.user)
            .select_related('turma__curso')
        )
        return Response(MatriculaAlunoListSerializer(qs, many=True).data)


class MatriculaAlunoDetailView(RetrieveAPIView):
    """Detalhe de uma matrícula do próprio aluno."""

    permission_classes = (IsAuthenticated, IsOwnerAluno)
    serializer_class = MatriculaAlunoDetailSerializer
    queryset = Matricula.objects.select_related('turma__curso').all()


class DocumentosUploadView(APIView):
    """Upload de documentos via token (sem autenticação)."""

    permission_classes = (AllowAny,)

    def post(self, request):
        token = request.data.get('token')
        tipos_validos = {c.value for c in Documento.Tipo}
        arquivos = {
            tipo: arquivo for tipo, arquivo in request.FILES.items()
            if tipo in tipos_validos
        }
        if not arquivos:
            return Response(
                {'detail': 'Envie ao menos um arquivo (RG, CPF ou HISTORICO_EM).'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        _matricula, docs = registrar_documentos(token, arquivos)
        return Response(
            DocumentoSerializer(docs, many=True, context={'request': request}).data,
            status=status.HTTP_201_CREATED,
        )


class MatriculaStatusView(APIView):
    """Consulta pública de status via token de upload."""

    permission_classes = (AllowAny,)

    def get(self, request):
        token = request.query_params.get('token')
        matricula = matricula_por_token(token)
        if matricula is None:
            raise NotFound('Matrícula não encontrada para este token.')
        return Response(
            MatriculaStatusSerializer(matricula, context={'request': request}).data
        )


class AsaasWebhookView(APIView):
    """Recebe notificações do Asaas. Verifica autenticidade antes de processar."""

    permission_classes = (AllowAny,)

    def post(self, request):
        if not webhook_autentico(request.headers):
            raise PermissionDenied('Webhook não autenticado.')
        resultado = processar_webhook(request.data)
        return Response(resultado, status=status.HTTP_200_OK)


class AdminMatriculaListView(ListAPIView):
    """Lista todas as matrículas (Admin), com filtros por status/turma/curso."""

    permission_classes = (IsAdmin,)
    serializer_class = MatriculaAdminSerializer

    def get_queryset(self):
        qs = Matricula.objects.select_related(
            'turma__curso', 'aluno__user'
        ).prefetch_related('documentos')
        p = self.request.query_params
        if p.get('status'):
            qs = qs.filter(status=p['status'])
        if p.get('turma'):
            qs = qs.filter(turma_id=p['turma'])
        if p.get('curso'):
            qs = qs.filter(turma__curso_id=p['curso'])
        return qs


class AdminMatriculaDetailView(RetrieveAPIView):
    """Detalhe completo de uma matrícula (Admin), com documentos."""

    permission_classes = (IsAdmin,)
    serializer_class = MatriculaAdminSerializer
    queryset = Matricula.objects.select_related(
        'turma__curso', 'aluno__user'
    ).prefetch_related('documentos').all()


class DocumentoDownloadView(APIView):
    """Download seguro de documento sensível (RG/CPF/histórico).

    Acesso restrito ao Admin ou ao próprio aluno dono da matrícula — os arquivos
    nunca são expostos por URL pública (conformidade LGPD).
    """

    permission_classes = (IsAuthenticated,)

    def get(self, request, pk):
        documento = get_object_or_404(
            Documento.objects.select_related('matricula__aluno'), pk=pk
        )
        user = request.user
        is_admin = user.is_superuser or user.role == User.Role.ADMIN
        aluno = getattr(user, 'aluno', None)
        is_dono = (
            user.role == User.Role.ALUNO
            and aluno is not None
            and documento.matricula.aluno_id == aluno.id
        )
        if not (is_admin or is_dono):
            raise PermissionDenied('Você não tem acesso a este documento.')

        return FileResponse(
            documento.arquivo.open('rb'),
            as_attachment=True,
            filename=f'{documento.tipo.lower()}-{documento.id}',
        )
