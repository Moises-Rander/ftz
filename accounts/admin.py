from django import forms
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


class ProfessorAdminForm(forms.ModelForm):
    """Permite editar o nome (que vive na conta/User) direto no cadastro do professor."""

    first_name = forms.CharField(label='Nome', max_length=150, required=True)
    last_name = forms.CharField(label='Sobrenome', max_length=150, required=False)

    class Meta:
        model = Professor
        fields = ('user', 'titulacao', 'bio', 'foto')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk and self.instance.user_id:
            self.fields['first_name'].initial = self.instance.user.first_name
            self.fields['last_name'].initial = self.instance.user.last_name


@admin.register(Professor)
class ProfessorAdmin(admin.ModelAdmin):
    form = ProfessorAdminForm
    list_display = ('nome_exibicao', 'titulacao', 'user')
    search_fields = ('user__email', 'user__first_name', 'user__last_name', 'titulacao')
    autocomplete_fields = ('user',)
    fields = ('user', 'first_name', 'last_name', 'titulacao', 'bio', 'foto')

    @admin.display(description='nome')
    def nome_exibicao(self, obj):
        return obj.user.get_full_name() or obj.user.email

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        # Grava o nome na conta (User) do professor — é o que o site exibe.
        user = obj.user
        user.first_name = form.cleaned_data.get('first_name', '')
        user.last_name = form.cleaned_data.get('last_name', '')
        user.save(update_fields=['first_name', 'last_name'])
