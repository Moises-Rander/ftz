from django.http import FileResponse, Http404
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from accounts.permissions import IsAdmin

from .models import CandidatoVestibular, EdicaoVestibular
from .serializers import (
    CandidatoAdminSerializer,
    CandidatoStatusUpdateSerializer,
    ConsultaStatusSerializer,
    EdicaoAdminSerializer,
    EdicaoPublicaSerializer,
    InscricaoSerializer,
    PublicarResultadoSerializer,
)
from .services import (
    atualizar_status_candidato,
    inscrever_candidato,
    publicar_resultado,
)


class EdicaoPublicViewSet(viewsets.ReadOnlyModelViewSet):
    """Público: lista/consulta edições, inscrição, status e download do resultado."""

    permission_classes = (AllowAny,)
    serializer_class = EdicaoPublicaSerializer
    queryset = EdicaoVestibular.objects.select_related('turma__curso').all()

    @action(detail=True, methods=['post'])
    def inscrever(self, request, pk=None):
        edicao = self.get_object()
        serializer = InscricaoSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        candidato = inscrever_candidato(edicao=edicao, **serializer.validated_data)
        return Response(
            {'id': candidato.id, 'status': candidato.status,
             'detail': 'Inscrição confirmada. Verifique seu email.'},
            status=status.HTTP_201_CREATED,
        )

    @action(detail=True, methods=['get'], url_path='consultar-status')
    def consultar_status(self, request, pk=None):
        edicao = self.get_object()
        serializer = ConsultaStatusSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        candidato = CandidatoVestibular.objects.filter(
            edicao=edicao, cpf=serializer.validated_data['cpf']
        ).first()
        if candidato is None:
            raise Http404('Inscrição não encontrada para este CPF nesta edição.')
        # Não expõe dados de outros candidatos — apenas o status.
        return Response({'status': candidato.status,
                         'status_display': candidato.get_status_display()})

    @action(detail=True, methods=['get'])
    def resultado(self, request, pk=None):
        edicao = self.get_object()
        if not edicao.pdf_disponivel:
            raise Http404('Resultado ainda não publicado.')
        return FileResponse(
            edicao.resultado_pdf.open('rb'), as_attachment=True,
            filename=f'resultado-vestibular-{edicao.id}.pdf',
        )


class EdicaoAdminViewSet(viewsets.ModelViewSet):
    """Admin: CRUD de edições + publicação de resultado + candidatos."""

    permission_classes = (IsAdmin,)
    serializer_class = EdicaoAdminSerializer
    queryset = EdicaoVestibular.objects.select_related('turma__curso').all()

    def perform_destroy(self, instance):
        if instance.candidatos.exists():
            raise ValidationError(
                'Não é possível excluir uma edição que já possui candidatos inscritos.'
            )
        instance.delete()

    @action(detail=True, methods=['post'], url_path='publicar-resultado')
    def publicar(self, request, pk=None):
        edicao = self.get_object()
        serializer = PublicarResultadoSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        enviados, falhas = publicar_resultado(
            edicao, serializer.validated_data['resultado_pdf']
        )
        return Response(
            {'detail': 'Resultado publicado.', 'notificados': enviados, 'falhas': falhas},
            status=status.HTTP_200_OK,
        )

    @action(detail=True, methods=['get'])
    def candidatos(self, request, pk=None):
        edicao = self.get_object()
        qs = edicao.candidatos.all().order_by('id')
        status_filtro = request.query_params.get('status')
        if status_filtro:
            qs = qs.filter(status=status_filtro)
        return Response(CandidatoAdminSerializer(qs, many=True).data)


class CandidatoAdminViewSet(viewsets.ModelViewSet):
    """Admin: lista/detalhe de candidatos e atualização de status."""

    permission_classes = (IsAdmin,)
    serializer_class = CandidatoAdminSerializer
    queryset = CandidatoVestibular.objects.select_related('edicao__turma').all()
    http_method_names = ('get', 'patch', 'head', 'options')

    def get_queryset(self):
        qs = super().get_queryset()
        p = self.request.query_params
        if p.get('edicao'):
            qs = qs.filter(edicao_id=p['edicao'])
        if p.get('status'):
            qs = qs.filter(status=p['status'])
        return qs.order_by('id')

    def partial_update(self, request, *args, **kwargs):
        candidato = self.get_object()
        serializer = CandidatoStatusUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        candidato = atualizar_status_candidato(
            candidato, serializer.validated_data['status']
        )
        return Response(CandidatoAdminSerializer(candidato).data)
