from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    AtribuicaoProfessorAdminViewSet,
    CicloAdminViewSet,
    CursoAdminViewSet,
    CursoPublicViewSet,
    DisciplinaAdminViewSet,
    GradeHorariaAdminViewSet,
    HorarioFormacaoAdminViewSet,
    ModuloAdminViewSet,
    ProgressoModuloTurmaAdminViewSet,
    TurmaAdminViewSet,
    TurmaPublicViewSet,
)

app_name = 'cursos'

# Endpoints públicos / de leitura
public_router = DefaultRouter()
public_router.register('cursos', CursoPublicViewSet, basename='curso')
public_router.register('turmas', TurmaPublicViewSet, basename='turma')

# Endpoints de gerenciamento (somente Admin)
admin_router = DefaultRouter()
admin_router.register('cursos', CursoAdminViewSet, basename='admin-curso')
admin_router.register('turmas', TurmaAdminViewSet, basename='admin-turma')
admin_router.register('disciplinas', DisciplinaAdminViewSet, basename='admin-disciplina')
admin_router.register('ciclos', CicloAdminViewSet, basename='admin-ciclo')
admin_router.register('grade-horaria', GradeHorariaAdminViewSet, basename='admin-grade')
admin_router.register('modulos', ModuloAdminViewSet, basename='admin-modulo')
admin_router.register(
    'progresso-modulos', ProgressoModuloTurmaAdminViewSet, basename='admin-progresso'
)
admin_router.register(
    'horarios-formacao', HorarioFormacaoAdminViewSet, basename='admin-horario'
)
admin_router.register(
    'atribuicoes', AtribuicaoProfessorAdminViewSet, basename='admin-atribuicao'
)

urlpatterns = public_router.urls + [
    path('admin/', include((admin_router.urls, 'admin'))),
]
