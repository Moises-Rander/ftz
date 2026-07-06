from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _

from .models import Aluno, Professor, User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Admin do usuário base com login por email (sem username)."""

    ordering = ('email',)
    list_display = ('email', 'first_name', 'last_name', 'role', 'is_staff', 'is_active')
    list_filter = ('role', 'is_staff', 'is_superuser', 'is_active')
    search_fields = ('email', 'first_name', 'last_name')

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Informações pessoais'), {'fields': ('first_name', 'last_name')}),
        (_('Perfil'), {'fields': ('role',)}),
        (_('Permissões'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        (_('Datas importantes'), {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'role', 'password1', 'password2'),
        }),
    )


@admin.register(Aluno)
class AlunoAdmin(admin.ModelAdmin):
    list_display = ('user', 'cpf', 'telefone', 'data_nascimento')
    search_fields = ('user__email', 'user__first_name', 'user__last_name', 'cpf', 'rg')
    list_filter = ('data_nascimento',)
    autocomplete_fields = ('user',)


@admin.register(Professor)
class ProfessorAdmin(admin.ModelAdmin):
    list_display = ('user', 'titulacao')
    search_fields = ('user__email', 'user__first_name', 'user__last_name', 'titulacao')
    autocomplete_fields = ('user',)
