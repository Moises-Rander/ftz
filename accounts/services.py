"""Serviços reutilizáveis de conta de usuário.

Centraliza a criação de contas de Aluno (usada na aprovação de matrícula no V4)
e o envio de links de senha (definição inicial e redefinição), ambos apoiados
no gerador de tokens padrão do Django (validade controlada por
``PASSWORD_RESET_TIMEOUT``).
"""
from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.db import transaction
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from notifications.emails import EmailType
from notifications.services import enviar_notificacao

from .models import Aluno, User


def montar_link_senha(user):
    """Monta uid+token e o link de front-end para definir/redefinir a senha."""
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)
    base = settings.FRONTEND_URL.rstrip('/') + settings.PASSWORD_RESET_PATH
    link = f'{base}?uid={uid}&token={token}'
    return uid, token, link


def enviar_email_senha(user, *, definir_inicial=False):
    """Envia o email com o link de senha via serviço central de notificações.

    ``definir_inicial=True`` usa o email de primeiro acesso do aluno aprovado;
    caso contrário, é uma redefinição comum.
    """
    _uid, _token, link = montar_link_senha(user)
    nome = user.get_full_name() or user.email
    tipo = (
        EmailType.CONTA_DEFINIR_SENHA if definir_inicial
        else EmailType.CONTA_RECUPERAR_SENHA
    )
    enviar_notificacao(tipo, user.email, {'nome': nome, 'link': link})
    return link


@transaction.atomic
def criar_usuario_aluno(*, email, cpf, first_name='', last_name='', rg='',
                        telefone='', data_nascimento=None, enviar_email=True):
    """Cria User (role ALUNO, sem senha utilizável) + perfil Aluno.

    O aluno define a própria senha via link enviado por email — reaproveitando
    o fluxo de recuperação de senha. Reutilizável pela aprovação de matrícula
    (V4). Se o usuário já existir, reaproveita-o (idempotente por email).
    """
    user, criado = User.objects.get_or_create(
        email=email,
        defaults={
            'role': User.Role.ALUNO,
            'first_name': first_name,
            'last_name': last_name,
        },
    )
    if criado:
        user.set_unusable_password()
        user.save(update_fields=['password'])

    aluno, _ = Aluno.objects.get_or_create(
        user=user,
        defaults={
            'cpf': cpf,
            'rg': rg,
            'telefone': telefone,
            'data_nascimento': data_nascimento,
        },
    )

    if criado and enviar_email:
        enviar_email_senha(user, definir_inicial=True)

    return aluno
