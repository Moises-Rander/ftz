from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    AlunoAvaliacoesView,
    AlunoBoletimView,
    AlunoEntregarView,
    AlunoFrequenciaView,
    AlunoMinhaEntregaView,
    AlunoTrabalhosView,
    AlunoTurmaAulasView,
    AulaAdminViewSet,
    AulaFrequenciaView,
    AvaliacaoAdminViewSet,
    AvaliacaoResultadosView,
    AvaliacoesProfessorView,
    EntregaCorrigirView,
    ProfessorTurmaAlunosView,
    ProfessorTurmaAulasView,
    ProfessorTurmasView,
    TrabalhoAdminViewSet,
    TrabalhoEntregasView,
    TrabalhosProfessorView,
)

app_name = 'academico'

# Admin — /api/admin/academico/
admin_router = DefaultRouter()
admin_router.register('aulas', AulaAdminViewSet, basename='admin-aula')
admin_router.register('avaliacoes', AvaliacaoAdminViewSet, basename='admin-avaliacao')
admin_router.register('trabalhos', TrabalhoAdminViewSet, basename='admin-trabalho')

professor_urls = [
    path('turmas/', ProfessorTurmasView.as_view(), name='prof-turmas'),
    path('turmas/<int:turma_id>/aulas/', ProfessorTurmaAulasView.as_view(), name='prof-turma-aulas'),
    path('turmas/<int:turma_id>/alunos/', ProfessorTurmaAlunosView.as_view(), name='prof-turma-alunos'),
    path('aulas/<int:aula_id>/frequencia/', AulaFrequenciaView.as_view(), name='prof-frequencia'),
    path('avaliacoes/', AvaliacoesProfessorView.as_view(), name='prof-avaliacoes'),
    path('avaliacoes/<int:avaliacao_id>/resultados/', AvaliacaoResultadosView.as_view(), name='prof-resultados'),
    path('trabalhos/', TrabalhosProfessorView.as_view(), name='prof-trabalhos'),
    path('trabalhos/<int:trabalho_id>/entregas/', TrabalhoEntregasView.as_view(), name='prof-entregas'),
    path('entregas/<int:entrega_id>/', EntregaCorrigirView.as_view(), name='prof-corrigir'),
]

aluno_urls = [
    path('turmas/<int:turma_id>/aulas/', AlunoTurmaAulasView.as_view(), name='aluno-aulas'),
    path('turmas/<int:turma_id>/frequencia/', AlunoFrequenciaView.as_view(), name='aluno-frequencia'),
    path('turmas/<int:turma_id>/avaliacoes/', AlunoAvaliacoesView.as_view(), name='aluno-avaliacoes'),
    path('turmas/<int:turma_id>/trabalhos/', AlunoTrabalhosView.as_view(), name='aluno-trabalhos'),
    path('trabalhos/<int:trabalho_id>/entregar/', AlunoEntregarView.as_view(), name='aluno-entregar'),
    path('trabalhos/<int:trabalho_id>/minha-entrega/', AlunoMinhaEntregaView.as_view(), name='aluno-minha-entrega'),
    path('turmas/<int:turma_id>/boletim/', AlunoBoletimView.as_view(), name='aluno-boletim'),
]

urlpatterns = [
    path('admin/academico/', include((admin_router.urls, 'admin'))),
    path('professor/', include((professor_urls, 'professor'))),
    path('aluno/', include((aluno_urls, 'aluno'))),
]
