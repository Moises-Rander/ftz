from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken

from .models import Aluno, Professor, User


class UserBasicSerializer(serializers.ModelSerializer):
    """Dados básicos do usuário retornados no login e no perfil de Admin."""

    nome = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'nome', 'email', 'role')

    def get_nome(self, obj):
        return obj.get_full_name() or obj.email


class LoginSerializer(TokenObtainPairSerializer):
    """Login por email/senha. Retorna tokens + dados básicos do usuário."""

    default_error_messages = {
        'no_active_account': 'Email ou senha inválidos, ou conta inativa.',
    }

    def validate(self, attrs):
        data = super().validate(attrs)
        data['user'] = UserBasicSerializer(self.user).data
        return data


class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()

    def validate(self, attrs):
        self.token = attrs['refresh']
        return attrs

    def save(self, **kwargs):
        try:
            RefreshToken(self.token).blacklist()
        except Exception:
            raise serializers.ValidationError({'refresh': 'Token inválido ou já expirado.'})


class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()


class PasswordResetConfirmSerializer(serializers.Serializer):
    """Confirma a redefinição: valida uid+token (link), expiração e troca a senha."""

    uid = serializers.CharField()
    token = serializers.CharField()
    new_password = serializers.CharField(write_only=True)
    new_password_confirm = serializers.CharField(write_only=True)

    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError(
                {'new_password_confirm': 'As senhas não conferem.'}
            )

        try:
            uid = force_str(urlsafe_base64_decode(attrs['uid']))
            user = User.objects.get(pk=uid)
        except (User.DoesNotExist, ValueError, TypeError, OverflowError):
            raise serializers.ValidationError({'uid': 'Link inválido.'})

        # check_token também verifica a validade de 24h (PASSWORD_RESET_TIMEOUT)
        # e o token deixa de valer após a troca de senha (descartado após o uso).
        if not default_token_generator.check_token(user, attrs['token']):
            raise serializers.ValidationError(
                {'token': 'Link inválido ou expirado. Solicite um novo.'}
            )

        validate_password(attrs['new_password'], user)
        self.user = user
        return attrs

    def save(self, **kwargs):
        self.user.set_password(self.validated_data['new_password'])
        self.user.save(update_fields=['password'])
        return self.user


class _PerfilBaseSerializer(serializers.ModelSerializer):
    """Base para perfis: expõe campos do User e impede edição de email/role."""

    id = serializers.IntegerField(source='user.id', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)
    role = serializers.CharField(source='user.role', read_only=True)
    first_name = serializers.CharField(
        source='user.first_name', required=False, allow_blank=True
    )
    last_name = serializers.CharField(
        source='user.last_name', required=False, allow_blank=True
    )

    def update(self, instance, validated_data):
        user_data = validated_data.pop('user', {})
        if user_data:
            for attr, value in user_data.items():
                setattr(instance.user, attr, value)
            instance.user.save()
        return super().update(instance, validated_data)


class ChangePasswordSerializer(serializers.Serializer):
    """Troca de senha do usuário autenticado (senha atual + nova)."""

    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True)
    new_password_confirm = serializers.CharField(write_only=True)

    def validate(self, attrs):
        user = self.context['request'].user
        if not user.check_password(attrs['old_password']):
            raise serializers.ValidationError({'old_password': 'Senha atual incorreta.'})
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError(
                {'new_password_confirm': 'As senhas não conferem.'}
            )
        validate_password(attrs['new_password'], user)
        return attrs

    def save(self, **kwargs):
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.save(update_fields=['password'])
        return user


class AlunoProfileSerializer(_PerfilBaseSerializer):
    class Meta:
        model = Aluno
        fields = (
            'id', 'email', 'role', 'first_name', 'last_name',
            'cpf', 'rg', 'telefone', 'data_nascimento', 'foto',
        )
        # CPF é identidade — gerenciado pelo admin, não editável aqui.
        read_only_fields = ('cpf',)


class ProfessorProfileSerializer(_PerfilBaseSerializer):
    class Meta:
        model = Professor
        fields = (
            'id', 'email', 'role', 'first_name', 'last_name',
            'bio', 'titulacao', 'foto',
        )
