from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone


class AtividadeTurmaBase(models.Model):
    """Base para itens vinculados a uma Turma e a uma Disciplina (Graduação) OU
    a um Módulo (Formação) — exatamente um dos dois."""

    turma = models.ForeignKey(
        'cursos.Turma', on_delete=models.CASCADE,
        related_name='%(class)ss', verbose_name='turma',
    )
    disciplina = models.ForeignKey(
        'cursos.Disciplina', on_delete=models.CASCADE, null=True, blank=True,
        related_name='%(class)ss', verbose_name='disciplina',
    )
    modulo = models.ForeignKey(
        'cursos.Modulo', on_delete=models.CASCADE, null=True, blank=True,
        related_name='%(class)ss', verbose_name='módulo',
    )

    class Meta:
        abstract = True

    def _validar_disciplina_xor_modulo(self):
        if bool(self.disciplina_id) == bool(self.modulo_id):
            raise ValidationError(
                'Preencha exatamente um entre Disciplina (Graduação) e Módulo (Formação).'
            )
        if self.disciplina_id and self.turma_id and self.disciplina.curso_id != self.turma.curso_id:
            raise ValidationError({'disciplina': 'A disciplina deve ser do mesmo curso da turma.'})
        if self.modulo_id and self.turma_id and self.modulo.curso_id != self.turma.curso_id:
            raise ValidationError({'modulo': 'O módulo deve pertencer ao mesmo curso da turma.'})

    def clean(self):
        self._validar_disciplina_xor_modulo()


class Aula(AtividadeTurmaBase):
    """Ocorrência real de uma aula em uma Turma."""

    # Ciclo aplica-se apenas à Graduação.
    ciclo = models.ForeignKey(
        'cursos.Ciclo', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='aulas', verbose_name='ciclo',
    )
    data = models.DateField('data')
    horario_inicio = models.TimeField('horário de início')
    duracao_minutos = models.PositiveSmallIntegerField('duração (min)', default=60)
    cancelada = models.BooleanField('cancelada', default=False)
    motivo_cancelamento = models.TextField('motivo do cancelamento', null=True, blank=True)

    class Meta:
        verbose_name = 'aula'
        verbose_name_plural = 'aulas'
        ordering = ['-data', 'horario_inicio']

    def __str__(self):
        alvo = self.disciplina or self.modulo
        return f'{alvo} — {self.data:%d/%m/%Y} {self.horario_inicio:%H:%M}'

    def clean(self):
        super().clean()
        if self.ciclo_id:
            if self.disciplina_id is None:
                raise ValidationError({'ciclo': 'Ciclo só se aplica a aulas de Graduação (disciplina).'})
            if self.turma_id and self.ciclo.turma_id != self.turma_id:
                raise ValidationError({'ciclo': 'O ciclo deve pertencer à turma da aula.'})
        if self.cancelada and not self.motivo_cancelamento:
            raise ValidationError(
                {'motivo_cancelamento': 'Informe o motivo ao cancelar a aula.'}
            )


class Frequencia(models.Model):
    """Presença de um Aluno em uma Aula, lançada por um Professor."""

    aula = models.ForeignKey(
        Aula, on_delete=models.CASCADE, related_name='frequencias', verbose_name='aula'
    )
    aluno = models.ForeignKey(
        'accounts.Aluno', on_delete=models.CASCADE,
        related_name='frequencias', verbose_name='aluno',
    )
    presente = models.BooleanField('presente', default=False)
    lancado_por = models.ForeignKey(
        'accounts.Professor', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='frequencias_lancadas', verbose_name='lançada por',
    )

    class Meta:
        verbose_name = 'frequência'
        verbose_name_plural = 'frequências'
        constraints = [
            models.UniqueConstraint(fields=['aula', 'aluno'], name='frequencia_unica_aula_aluno')
        ]

    def __str__(self):
        marca = 'presente' if self.presente else 'ausente'
        return f'{self.aluno} — {marca} ({self.aula})'


class Avaliacao(AtividadeTurmaBase):
    titulo = models.CharField('título', max_length=200)
    descricao = models.TextField('descrição', blank=True)
    data = models.DateField('data')
    nota_maxima = models.DecimalField('nota máxima', max_digits=5, decimal_places=2, default=10)

    class Meta:
        verbose_name = 'avaliação'
        verbose_name_plural = 'avaliações'
        ordering = ['-data']

    def __str__(self):
        return self.titulo


class ResultadoAvaliacao(models.Model):
    avaliacao = models.ForeignKey(
        Avaliacao, on_delete=models.CASCADE, related_name='resultados', verbose_name='avaliação'
    )
    aluno = models.ForeignKey(
        'accounts.Aluno', on_delete=models.CASCADE,
        related_name='resultados_avaliacao', verbose_name='aluno',
    )
    nota = models.DecimalField('nota', max_digits=5, decimal_places=2)
    lancado_por = models.ForeignKey(
        'accounts.Professor', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='resultados_lancados', verbose_name='lançada por',
    )

    class Meta:
        verbose_name = 'resultado de avaliação'
        verbose_name_plural = 'resultados de avaliação'
        constraints = [
            models.UniqueConstraint(
                fields=['avaliacao', 'aluno'], name='resultado_unico_avaliacao_aluno'
            )
        ]

    def __str__(self):
        return f'{self.aluno} — {self.nota} ({self.avaliacao})'

    def clean(self):
        if self.avaliacao_id and self.nota is not None and self.nota > self.avaliacao.nota_maxima:
            raise ValidationError({'nota': 'A nota não pode exceder a nota máxima da avaliação.'})


class Trabalho(AtividadeTurmaBase):
    titulo = models.CharField('título', max_length=200)
    descricao = models.TextField('descrição', blank=True)
    prazo_entrega = models.DateTimeField('prazo de entrega')
    arquivo_enunciado = models.FileField(
        'arquivo de enunciado', upload_to='trabalhos/enunciados/', null=True, blank=True
    )

    class Meta:
        verbose_name = 'trabalho'
        verbose_name_plural = 'trabalhos'
        ordering = ['-prazo_entrega']

    def __str__(self):
        return self.titulo


class EntregaTrabalho(models.Model):
    trabalho = models.ForeignKey(
        Trabalho, on_delete=models.CASCADE, related_name='entregas', verbose_name='trabalho'
    )
    aluno = models.ForeignKey(
        'accounts.Aluno', on_delete=models.CASCADE,
        related_name='entregas_trabalho', verbose_name='aluno',
    )
    arquivo = models.FileField('arquivo enviado', upload_to='trabalhos/entregas/')
    # Definido no envio (atualiza a cada reenvio antes da correção).
    data_hora_entrega = models.DateTimeField('entregue em', default=timezone.now)
    entregue_em_atraso = models.BooleanField('entregue em atraso', default=False)
    nota = models.DecimalField('nota', max_digits=5, decimal_places=2, null=True, blank=True)
    feedback = models.TextField('feedback', null=True, blank=True)

    class Meta:
        verbose_name = 'entrega de trabalho'
        verbose_name_plural = 'entregas de trabalho'
        constraints = [
            models.UniqueConstraint(
                fields=['trabalho', 'aluno'], name='entrega_unica_trabalho_aluno'
            )
        ]

    def __str__(self):
        return f'{self.aluno} — {self.trabalho}'

    @property
    def corrigida(self):
        return self.nota is not None
