from django.core.exceptions import ValidationError
from django.db import models


class EdicaoVestibular(models.Model):
    """Edição de vestibular de uma Turma de Graduação."""

    turma = models.ForeignKey(
        'cursos.Turma', on_delete=models.CASCADE,
        related_name='edicoes_vestibular', verbose_name='turma',
    )
    data_prova = models.DateField('data da prova')
    local_prova = models.CharField('local da prova', max_length=255)
    prazo_matricula = models.DateField('prazo de matrícula após aprovação')
    resultado_pdf = models.FileField(
        'PDF de resultado', upload_to='vestibular/resultados/', null=True, blank=True
    )
    resultado_publicado = models.BooleanField('resultado publicado', default=False)
    data_criacao = models.DateTimeField('criada em', auto_now_add=True)

    class Meta:
        verbose_name = 'edição de vestibular'
        verbose_name_plural = 'edições de vestibular'
        ordering = ['-data_prova']

    def __str__(self):
        return f'Vestibular {self.turma} — {self.data_prova:%d/%m/%Y}'

    @property
    def pdf_disponivel(self):
        """O PDF só fica disponível no site quando o resultado é publicado."""
        return bool(self.resultado_pdf) and self.resultado_publicado

    def clean(self):
        if self.turma_id and not self.turma.curso.is_graduacao:
            raise ValidationError('Vestibular só se aplica a turmas de Graduação.')
        if self.resultado_publicado and not self.resultado_pdf:
            raise ValidationError(
                {'resultado_publicado': 'Anexe o PDF de resultado antes de publicá-lo.'}
            )


class CandidatoVestibular(models.Model):
    """Candidato inscrito em uma edição de vestibular. Ainda não é usuário do sistema."""

    class Status(models.TextChoices):
        INSCRITO = 'INSCRITO', 'Inscrito'
        APROVADO = 'APROVADO', 'Aprovado'
        REPROVADO = 'REPROVADO', 'Reprovado'
        LISTA_ESPERA = 'LISTA_ESPERA', 'Lista de espera'
        DESISTIU = 'DESISTIU', 'Desistiu'

    edicao = models.ForeignKey(
        EdicaoVestibular, on_delete=models.CASCADE,
        related_name='candidatos', verbose_name='edição',
    )
    nome = models.CharField('nome', max_length=150)
    email = models.EmailField('email')
    cpf = models.CharField('CPF', max_length=14)
    telefone = models.CharField('telefone', max_length=20, blank=True)
    status = models.CharField(
        'status', max_length=15, choices=Status.choices, default=Status.INSCRITO
    )
    notificado_por_email = models.BooleanField('notificado por email', default=False)

    class Meta:
        verbose_name = 'candidato de vestibular'
        verbose_name_plural = 'candidatos de vestibular'
        ordering = ['nome']
        constraints = [
            models.UniqueConstraint(
                fields=['edicao', 'cpf'], name='candidato_unico_por_edicao_cpf'
            )
        ]

    def __str__(self):
        return f'{self.nome} ({self.get_status_display()})'
