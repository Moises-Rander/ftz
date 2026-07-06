from rest_framework import status
from rest_framework.generics import RetrieveUpdateAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView

from .models import User
from .serializers import (
    AlunoProfileSerializer,
    ChangePasswordSerializer,
    LoginSerializer,
    LogoutSerializer,
    PasswordResetConfirmSerializer,
    PasswordResetRequestSerializer,
    ProfessorProfileSerializer,
    UserBasicSerializer,
)
from .services import enviar_email_senha

# Resposta genérica de recuperação: nunca revela se o email existe.
_RESET_GENERIC_MSG = (
    'Se houver uma conta com este email, enviaremos um link de redefinição '
    'de senha.'
)


class LoginView(TokenObtainPairView):
    """POST email/senha -> access, refresh e dados básicos do usuário."""

    permission_classes = (AllowAny,)
    serializer_class = LoginSerializer
    throttle_scope = 'login'


class LogoutView(APIView):
    """POST refresh -> invalida (blacklist) o refresh token."""

    permission_classes = (IsAuthenticated,)

    def post(self, request):
        serializer = LogoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_205_RESET_CONTENT)


class PasswordResetRequestView(APIView):
    """POST email -> dispara o link de redefinição (resposta sempre genérica)."""

    permission_classes = (AllowAny,)
    throttle_scope = 'password_reset'

    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']

        user = User.objects.filter(email__iexact=email, is_active=True).first()
        if user is not None and user.has_usable_password():
            enviar_email_senha(user, definir_inicial=False)
        elif user is not None:
            # Conta criada mas sem senha definida ainda (ex.: aluno aprovado).
            enviar_email_senha(user, definir_inicial=True)

        return Response({'detail': _RESET_GENERIC_MSG}, status=status.HTTP_200_OK)


class PasswordResetConfirmView(APIView):
    """POST uid+token+nova senha -> valida e atualiza a senha."""

    permission_classes = (AllowAny,)
    throttle_scope = 'password_reset'

    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {'detail': 'Senha redefinida com sucesso.'}, status=status.HTTP_200_OK
        )


class ChangePasswordView(APIView):
    """POST senha atual + nova -> troca a senha do usuário autenticado."""

    permission_classes = (IsAuthenticated,)

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'detail': 'Senha alterada com sucesso.'}, status=status.HTTP_200_OK)


class ProfileView(RetrieveUpdateAPIView):
    """GET/PATCH do perfil do próprio usuário autenticado.

    Aluno -> campos de Aluno; Professor -> campos de Professor; Admin -> dados
    básicos. ``role`` nunca é editável (somente leitura nos serializers).
    """

    permission_classes = (IsAuthenticated,)
    http_method_names = ('get', 'patch', 'head', 'options')

    def get_serializer_class(self):
        user = self.request.user
        if user.role == User.Role.ALUNO and hasattr(user, 'aluno'):
            return AlunoProfileSerializer
        if user.role == User.Role.PROFESSOR and hasattr(user, 'professor'):
            return ProfessorProfileSerializer
        return UserBasicSerializer

    def get_object(self):
        user = self.request.user
        if user.role == User.Role.ALUNO and hasattr(user, 'aluno'):
            return user.aluno
        if user.role == User.Role.PROFESSOR and hasattr(user, 'professor'):
            return user.professor
        return user
