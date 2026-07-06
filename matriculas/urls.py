from django.urls import path

from .views import (
    AdminMatriculaDetailView,
    AdminMatriculaListView,
    AsaasWebhookView,
    DocumentoDownloadView,
    DocumentosUploadView,
    MatriculaAlunoDetailView,
    MatriculaStatusView,
    MatriculasView,
)

app_name = 'matriculas'

urlpatterns = [
    # Público / candidato
    path('matriculas/', MatriculasView.as_view(), name='matriculas'),
    path('matriculas/documentos/', DocumentosUploadView.as_view(), name='documentos'),
    path('matriculas/status/', MatriculaStatusView.as_view(), name='status'),
    path('matriculas/documentos/<int:pk>/download/', DocumentoDownloadView.as_view(),
         name='documento-download'),
    path('webhooks/asaas/', AsaasWebhookView.as_view(), name='webhook-asaas'),
    # Aluno
    path('matriculas/<int:pk>/', MatriculaAlunoDetailView.as_view(), name='matricula-detail'),
    # Admin
    path('admin/matriculas/', AdminMatriculaListView.as_view(), name='admin-matriculas'),
    path('admin/matriculas/<int:pk>/', AdminMatriculaDetailView.as_view(),
         name='admin-matricula-detail'),
]
