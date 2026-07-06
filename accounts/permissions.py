"""Permissões customizadas por perfil de usuário.

Resumo:
- IsAdmin / IsProfessor / IsAluno — restringem por ``role``.
- IsAdminOrReadOnly — Admin escreve; demais autenticados só leem.
- IsOwnerAluno — Aluno só acessa os próprios recursos; Admin acessa tudo.
- IsAtribuidoProfessor — Professor só acessa recursos de turmas atribuídas a
  ele; Admin acessa tudo.
"""
from rest_framework.permissions import SAFE_METHODS, BasePermission

from .models import User


def _is_admin(user):
    return bool(
        user and user.is_authenticated
        and (user.is_superuser or user.role == User.Role.ADMIN)
    )


def _resolver_aluno(obj):
    """Descobre o Aluno dono de ``obj`` percorrendo relações conhecidas."""
    if obj.__class__.__name__ == 'Aluno':
        return obj
    if hasattr(obj, 'aluno_id'):
        return getattr(obj, 'aluno', None)
    # Documento -> matricula -> aluno
    matricula = getattr(obj, 'matricula', None)
    if matricula is not None:
        return getattr(matricula, 'aluno', None)
    return None


def _resolver_turma(obj):
    """Descobre a Turma associada a ``obj`` percorrendo relações conhecidas."""
    if obj.__class__.__name__ == 'Turma':
        return obj
    if hasattr(obj, 'turma_id') and obj.turma_id:
        return getattr(obj, 'turma', None)
    # Encadeamentos: documento/matricula, frequencia/aula, resultado/avaliacao,
    # entrega/trabalho.
    for attr in ('matricula', 'aula', 'avaliacao', 'trabalho'):
        intermediario = getattr(obj, attr, None)
        if intermediario is not None:
            turma = getattr(intermediario, 'turma', None)
            if turma is not None:
                return turma
    return None


class IsAdmin(BasePermission):
    message = 'Apenas administradores têm acesso.'

    def has_permission(self, request, view):
        return _is_admin(request.user)


class IsProfessor(BasePermission):
    message = 'Apenas professores têm acesso.'

    def has_permission(self, request, view):
        user = request.user
        return bool(user and user.is_authenticated and user.role == User.Role.PROFESSOR)


class IsAluno(BasePermission):
    message = 'Apenas alunos têm acesso.'

    def has_permission(self, request, view):
        user = request.user
        return bool(user and user.is_authenticated and user.role == User.Role.ALUNO)


class IsAdminOrReadOnly(BasePermission):
    """Admin: acesso total. Demais autenticados: somente leitura."""

    def has_permission(self, request, view):
        user = request.user
        if not (user and user.is_authenticated):
            return False
        if request.method in SAFE_METHODS:
            return True
        return _is_admin(user)


class IsOwnerAluno(BasePermission):
    """Aluno só acessa recursos que lhe pertencem. Admin acessa tudo."""

    message = 'Você não tem acesso a este recurso.'

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        user = request.user
        if _is_admin(user):
            return True
        if user.role != User.Role.ALUNO:
            return False
        aluno = getattr(user, 'aluno', None)
        if aluno is None:
            return False
        # Para uma Turma, "pertencer" = ter matrícula APROVADA nela.
        if obj.__class__.__name__ == 'Turma':
            return obj.matriculas.filter(aluno=aluno, status='APROVADA').exists()
        dono = _resolver_aluno(obj)
        return dono is not None and dono.pk == aluno.pk


class IsAtribuidoProfessor(BasePermission):
    """Professor só acessa recursos de turmas a ele atribuídas. Admin acessa tudo."""

    message = 'Você não está atribuído a esta turma.'

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        user = request.user
        if _is_admin(user):
            return True
        if user.role != User.Role.PROFESSOR:
            return False
        professor = getattr(user, 'professor', None)
        if professor is None:
            return False
        turma = _resolver_turma(obj)
        if turma is None:
            return False
        # Import tardio para evitar dependência circular na carga do app.
        from cursos.models import AtribuicaoProfessor
        return AtribuicaoProfessor.objects.filter(
            professor=professor, turma=turma
        ).exists()
