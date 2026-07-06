from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models


class UserManager(BaseUserManager):
    """Manager que usa o email como identificador único (sem username)."""

    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError('O email é obrigatório.')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', User.Role.ADMIN)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superusuário precisa ter is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superusuário precisa ter is_superuser=True.')
        return self._create_user(email, password, **extra_fields)


class User(AbstractUser):
    """Usuário base do sistema. Login por email; sem campo username."""

    class Role(models.TextChoices):
        ALUNO = 'ALUNO', 'Aluno'
        PROFESSOR = 'PROFESSOR', 'Professor'
        ADMIN = 'ADMIN', 'Admin'

    username = None
    email = models.EmailField('email', unique=True)
    role = models.CharField(
        'perfil', max_length=20, choices=Role.choices, default=Role.ALUNO
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    class Meta:
        verbose_name = 'usuário'
        verbose_name_plural = 'usuários'

    def __str__(self):
        full = self.get_full_name()
        return f'{full} <{self.email}>' if full else self.email


class Aluno(models.Model):
    """Perfil de aluno, vinculado 1-para-1 ao usuário base."""

    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name='aluno', verbose_name='usuário'
    )
    cpf = models.CharField('CPF', max_length=14, unique=True)
    rg = models.CharField('RG', max_length=20, blank=True)
    telefone = models.CharField('telefone', max_length=20, blank=True)
    data_nascimento = models.DateField('data de nascimento', null=True, blank=True)
    foto = models.ImageField('foto de perfil', upload_to='alunos/', null=True, blank=True)

    class Meta:
        verbose_name = 'aluno'
        verbose_name_plural = 'alunos'

    def __str__(self):
        return self.user.get_full_name() or self.user.email


class Professor(models.Model):
    """Perfil de professor, vinculado 1-para-1 ao usuário base."""

    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name='professor', verbose_name='usuário'
    )
    bio = models.TextField('bio', blank=True)
    titulacao = models.CharField('titulação', max_length=120, blank=True)
    foto = models.ImageField('foto', upload_to='professores/', null=True, blank=True)

    class Meta:
        verbose_name = 'professor'
        verbose_name_plural = 'professores'

    def __str__(self):
        return self.user.get_full_name() or self.user.email
