from django.core.exceptions import ValidationError
from django.db import models, transaction


class TipoCurso(models.TextChoices):
    GRADUACAO = 'GRADUACAO', 'Graduação'
    FORMACAO = 'FORMACAO', 'Formação'


class DiaSemana(models.TextChoices):
    SEG = 'SEG', 'Segunda-feira'
    TER = 'TER', 'Terça-feira'
    QUA = 'QUA', 'Quarta-feira'
    QUI = 'QUI', 'Quinta-feira'
    SEX = 'SEX', 'Sexta-feira'
    SAB = 'SAB', 'Sábado'


# Dias permitidos na grade da Graduação (aulas presenciais noturnas + sábado).
DIAS_GRADUACAO = [
    (DiaSemana.SEG.value, DiaSemana.SEG.label),
    (DiaSemana.QUA.value, DiaSemana.QUA.label),
    (DiaSemana.SAB.value, DiaSemana.SAB.label),
]


class Curso(models.Model):
    nome = models.CharField('nome', max_length=150)
    descricao = models.TextField('descrição', blank=True)
    imagem = models.ImageField('imagem', upload_to='cursos/', null=True, blank=True)
    tipo = models.CharField('tipo', max_length=20, choices=TipoCurso.choices)
    carga_horaria = models.PositiveIntegerField('carga horária (horas)', default=0)
    preco_base = models.DecimalField('preço base', max_digits=10, decimal_places=2)

    class Meta:
        verbose_name = 'curso'
        verbose_name_plural = 'cursos'
        ordering = ['nome']

    def __str__(self):
        return f'{self.nome} ({self.get_tipo_display()})'

    @property
    def is_graduacao(self):
        return self.tipo == TipoCurso.GRADUACAO

    @property
    def is_formacao(self):
        return self.tipo == TipoCurso.FORMACAO


class Turma(models.Model):
    class Status(models.TextChoices):
        ABERTA = 'ABERTA', 'Aberta'
        FECHADA = 'FECHADA', 'Fechada'
        ENCERRADA = 'ENCERRADA', 'Encerrada'

    curso = models.ForeignKey(
        Curso, on_delete=models.CASCADE, related_name='turmas', verbose_name='curso'
    )
    nome = models.CharField('nome/identificação', max_length=120, blank=True)
    vagas_totais = models.PositiveIntegerField('vagas totais', default=0)
    status = models.CharField(
        'status', max_length=20, choices=Status.choices, default=Status.ABERTA
    )
    # Aplicável apenas a turmas de Graduação (prazo de matrícula após o vestibular).
    prazo_matricula_pos_vestibular = models.DateField(
        'prazo de matrícula pós-vestibular', null=True, blank=True
    )

    class Meta:
        verbose_name = 'turma'
        verbose_name_plural = 'turmas'
        ordering = ['curso', 'nome']

    def __str__(self):
        return f'{self.curso.nome} — {self.nome or f"Turma #{self.pk}"}'

    @property
    def vagas_ocupadas(self):
        """Calculado a partir das matrículas APROVADAS desta turma."""
        return self.matriculas.filter(status='APROVADA').count()

    @property
    def vagas_disponiveis(self):
        return max(self.vagas_totais - self.vagas_ocupadas, 0)

    @property
    def lotada(self):
        return self.vagas_ocupadas >= self.vagas_totais

    def sincronizar_status_vagas(self, save=True):
        """Fecha a turma automaticamente ao atingir as vagas totais.

        Apenas fecha — nunca reabre: o Admin pode fechar uma turma com vagas
        manualmente e a reabertura também é uma ação manual (ver V3). Não
        altera turmas ENCERRADAS.
        """
        if self.status == self.Status.ENCERRADA:
            return
        if self.lotada and self.status == self.Status.ABERTA:
            self.status = self.Status.FECHADA
            if save:
                Turma.objects.filter(pk=self.pk).update(status=self.Status.FECHADA)

    def clean(self):
        if self.prazo_matricula_pos_vestibular and self.curso_id and not self.curso.is_graduacao:
            raise ValidationError(
                {'prazo_matricula_pos_vestibular':
                    'Prazo de matrícula pós-vestibular só se aplica a turmas de Graduação.'}
            )


class Disciplina(models.Model):
    """Disciplina pertence a um Curso de Graduação (currículo compartilhado)."""

    curso = models.ForeignKey(
        Curso, on_delete=models.CASCADE, related_name='disciplinas', verbose_name='curso'
    )
    nome = models.CharField('nome', max_length=150)
    descricao = models.TextField('descrição', blank=True)
    ementa = models.TextField('ementa', blank=True)

    class Meta:
        verbose_name = 'disciplina'
        verbose_name_plural = 'disciplinas'
        ordering = ['curso', 'nome']

    def __str__(self):
        return self.nome

    def clean(self):
        if self.curso_id and not self.curso.is_graduacao:
            raise ValidationError(
                {'curso': 'Disciplinas só podem pertencer a cursos de Graduação.'}
            )


class Ciclo(models.Model):
    """Período de 6 semanas de uma Turma de Graduação. Apenas um ciclo ativo por turma."""

    turma = models.ForeignKey(
        Turma, on_delete=models.CASCADE, related_name='ciclos', verbose_name='turma'
    )
    numero = models.PositiveIntegerField('número do ciclo')
    data_inicio = models.DateField('data de início')
    data_fim = models.DateField('data de fim')
    is_ativo = models.BooleanField('ativo', default=False)

    class Meta:
        verbose_name = 'ciclo'
        verbose_name_plural = 'ciclos'
        ordering = ['turma', 'numero']
        constraints = [
            models.UniqueConstraint(
                fields=['turma', 'numero'], name='ciclo_numero_unico_por_turma'
            ),
            # Garante no máximo um ciclo ativo por turma.
            models.UniqueConstraint(
                fields=['turma'],
                condition=models.Q(is_ativo=True),
                name='ciclo_unico_ativo_por_turma',
            ),
        ]

    def __str__(self):
        return f'{self.turma} — Ciclo {self.numero}'

    def ativar(self):
        """Ativa este ciclo, desativando qualquer outro ativo da mesma turma."""
        with transaction.atomic():
            Ciclo.objects.filter(turma=self.turma, is_ativo=True).exclude(
                pk=self.pk
            ).update(is_ativo=False)
            self.is_ativo = True
            self.save(update_fields=['is_ativo'])

    def clean(self):
        if self.turma_id and not self.turma.curso.is_graduacao:
            raise ValidationError('Ciclos só existem em turmas de Graduação.')
        if self.data_inicio and self.data_fim and self.data_fim < self.data_inicio:
            raise ValidationError({'data_fim': 'A data de fim não pode ser anterior ao início.'})
        if self.is_ativo and self.turma_id:
            outro = Ciclo.objects.filter(turma=self.turma, is_ativo=True).exclude(pk=self.pk)
            if outro.exists():
                raise ValidationError(
                    'Já existe um ciclo ativo nesta turma. Desative-o antes de ativar outro.'
                )


class GradeHoraria(models.Model):
    """Template de horários de um Ciclo: em qual dia/horário e quantos slots uma
    disciplina ocorre naquele ciclo."""

    ciclo = models.ForeignKey(
        Ciclo, on_delete=models.CASCADE, related_name='grades', verbose_name='ciclo'
    )
    disciplina = models.ForeignKey(
        Disciplina, on_delete=models.CASCADE, related_name='grades', verbose_name='disciplina'
    )
    dia_semana = models.CharField('dia da semana', max_length=3, choices=DIAS_GRADUACAO)
    horario = models.TimeField('horário de início')
    slots = models.PositiveSmallIntegerField('slots de aula', default=1)

    class Meta:
        verbose_name = 'grade horária'
        verbose_name_plural = 'grades horárias'
        ordering = ['ciclo', 'dia_semana', 'horario']
        constraints = [
            models.UniqueConstraint(
                fields=['ciclo', 'disciplina', 'dia_semana'],
                name='grade_unica_por_ciclo_disciplina_dia',
            )
        ]

    def __str__(self):
        return f'{self.disciplina} — {self.get_dia_semana_display()} {self.horario:%H:%M}'

    def clean(self):
        if self.disciplina_id and self.ciclo_id:
            if self.disciplina.curso_id != self.ciclo.turma.curso_id:
                raise ValidationError(
                    {'disciplina': 'A disciplina deve pertencer ao mesmo curso da turma do ciclo.'}
                )


class Modulo(models.Model):
    """Módulo do currículo de um Curso de Formação.

    Assim como a Disciplina na Graduação, o módulo é definido no nível do Curso
    e compartilhado por todas as turmas daquele curso. O estado de progresso
    (ativo/concluído) é rastreado por turma em ``ProgressoModuloTurma``.
    """

    curso = models.ForeignKey(
        Curso, on_delete=models.CASCADE, related_name='modulos', verbose_name='curso'
    )
    nome = models.CharField('nome', max_length=150)
    descricao = models.TextField('descrição', blank=True)
    ordem = models.PositiveIntegerField('ordem', default=1)

    class Meta:
        verbose_name = 'módulo'
        verbose_name_plural = 'módulos'
        ordering = ['curso', 'ordem']
        constraints = [
            models.UniqueConstraint(
                fields=['curso', 'ordem'], name='modulo_ordem_unica_por_curso'
            ),
        ]

    def __str__(self):
        return f'{self.nome} (#{self.ordem})'

    def clean(self):
        if self.curso_id and not self.curso.is_formacao:
            raise ValidationError(
                {'curso': 'Módulos só podem pertencer a cursos de Formação.'}
            )


class ProgressoModuloTurma(models.Model):
    """Estado de progresso de um Módulo dentro de uma Turma de Formação.

    Espelha o papel do Ciclo na Graduação: apenas um módulo pode estar ativo
    por turma por vez. O admin altera o estado manualmente.
    """

    class Status(models.TextChoices):
        PENDENTE = 'PENDENTE', 'Pendente'
        ATIVO = 'ATIVO', 'Ativo'
        CONCLUIDO = 'CONCLUIDO', 'Concluído'

    turma = models.ForeignKey(
        Turma, on_delete=models.CASCADE,
        related_name='progressos_modulo', verbose_name='turma',
    )
    modulo = models.ForeignKey(
        Modulo, on_delete=models.CASCADE,
        related_name='progressos', verbose_name='módulo',
    )
    status = models.CharField(
        'status', max_length=20, choices=Status.choices, default=Status.PENDENTE
    )
    is_ativo = models.BooleanField('ativo', default=False)

    class Meta:
        verbose_name = 'progresso de módulo na turma'
        verbose_name_plural = 'progressos de módulos nas turmas'
        ordering = ['turma', 'modulo']
        constraints = [
            models.UniqueConstraint(
                fields=['turma', 'modulo'], name='progresso_unico_por_turma_modulo'
            ),
            # Garante no máximo um módulo ativo por turma.
            models.UniqueConstraint(
                fields=['turma'],
                condition=models.Q(is_ativo=True),
                name='progresso_unico_ativo_por_turma',
            ),
        ]

    def __str__(self):
        return f'{self.turma} — {self.modulo} [{self.get_status_display()}]'

    def modulo_anterior(self):
        """Módulo imediatamente anterior na sequência do curso (ou None)."""
        return Modulo.objects.filter(
            curso=self.modulo.curso, ordem__lt=self.modulo.ordem
        ).order_by('-ordem').first()

    def ativar(self):
        """Ativa este módulo na turma.

        - Exige que o módulo anterior na sequência esteja CONCLUÍDO (exceto o
          primeiro, que pode ser ativado livremente).
        - Desativa o módulo atualmente ativo da turma, marcando-o como CONCLUÍDO.
        """
        anterior = self.modulo_anterior()
        if anterior is not None:
            prog_ant = ProgressoModuloTurma.objects.filter(
                turma=self.turma, modulo=anterior
            ).first()
            # O anterior precisa já ter sido iniciado: CONCLUÍDO, ou ATIVO (caso
            # em que esta ativação o concluirá). Bloqueia se ainda PENDENTE/inexistente.
            if prog_ant is None or prog_ant.status == self.Status.PENDENTE:
                raise ValidationError(
                    'O módulo anterior precisa estar concluído (ou ativo) antes de ativar este.'
                )
        with transaction.atomic():
            ProgressoModuloTurma.objects.filter(
                turma=self.turma, is_ativo=True
            ).exclude(pk=self.pk).update(
                status=self.Status.CONCLUIDO, is_ativo=False
            )
            self.status = self.Status.ATIVO
            self.is_ativo = True
            self.save(update_fields=['status', 'is_ativo'])

    def clean(self):
        if self.turma_id and not self.turma.curso.is_formacao:
            raise ValidationError('Progresso de módulo só existe em turmas de Formação.')
        if self.modulo_id and self.turma_id and self.modulo.curso_id != self.turma.curso_id:
            raise ValidationError(
                {'modulo': 'O módulo deve pertencer ao mesmo curso da turma.'}
            )
        # is_ativo e status=ATIVO andam juntos.
        if self.is_ativo and self.status != self.Status.ATIVO:
            raise ValidationError(
                {'is_ativo': 'Para marcar como ativo, o status deve ser ATIVO.'}
            )
        if self.is_ativo and self.turma_id:
            outro = ProgressoModuloTurma.objects.filter(
                turma=self.turma, is_ativo=True
            ).exclude(pk=self.pk)
            if outro.exists():
                raise ValidationError(
                    'Já existe um módulo ativo nesta turma. '
                    'Conclua/pause-o antes de ativar outro.'
                )


class HorarioFormacao(models.Model):
    """Horário das aulas de uma Turma de Formação (dois dias da semana)."""

    turma = models.ForeignKey(
        Turma, on_delete=models.CASCADE, related_name='horarios_formacao', verbose_name='turma'
    )
    dia_1 = models.CharField('primeiro dia', max_length=3, choices=DiaSemana.choices)
    dia_2 = models.CharField('segundo dia', max_length=3, choices=DiaSemana.choices)
    horario_inicio = models.TimeField('horário de início')
    duracao_minutos = models.PositiveSmallIntegerField('duração do slot (min)', default=60)

    class Meta:
        verbose_name = 'horário de formação'
        verbose_name_plural = 'horários de formação'

    def __str__(self):
        return f'{self.turma} — {self.get_dia_1_display()}/{self.get_dia_2_display()}'

    def clean(self):
        if self.turma_id and not self.turma.curso.is_formacao:
            raise ValidationError('Horário de Formação só se aplica a turmas de Formação.')
        if self.dia_1 and self.dia_2 and self.dia_1 == self.dia_2:
            raise ValidationError({'dia_2': 'Os dois dias da semana devem ser diferentes.'})


class AtribuicaoProfessor(models.Model):
    """Vincula um Professor a uma Turma e a uma Disciplina (Graduação) OU a um
    Módulo (Formação) — exatamente um dos dois."""

    professor = models.ForeignKey(
        'accounts.Professor', on_delete=models.CASCADE,
        related_name='atribuicoes', verbose_name='professor',
    )
    turma = models.ForeignKey(
        Turma, on_delete=models.CASCADE, related_name='atribuicoes', verbose_name='turma'
    )
    disciplina = models.ForeignKey(
        Disciplina, on_delete=models.CASCADE, null=True, blank=True,
        related_name='atribuicoes', verbose_name='disciplina',
    )
    modulo = models.ForeignKey(
        Modulo, on_delete=models.CASCADE, null=True, blank=True,
        related_name='atribuicoes', verbose_name='módulo',
    )

    class Meta:
        verbose_name = 'atribuição de professor'
        verbose_name_plural = 'atribuições de professores'
        constraints = [
            # Exatamente um entre disciplina e módulo deve estar preenchido.
            models.CheckConstraint(
                name='atribuicao_disciplina_xor_modulo',
                condition=(
                    models.Q(disciplina__isnull=False, modulo__isnull=True)
                    | models.Q(disciplina__isnull=True, modulo__isnull=False)
                ),
            ),
        ]

    def __str__(self):
        alvo = self.disciplina or self.modulo
        return f'{self.professor} → {alvo} ({self.turma})'

    def clean(self):
        if bool(self.disciplina_id) == bool(self.modulo_id):
            raise ValidationError(
                'Preencha exatamente um entre Disciplina (Graduação) e Módulo (Formação).'
            )
        if self.disciplina_id and self.turma_id and self.disciplina.curso_id != self.turma.curso_id:
            raise ValidationError({'disciplina': 'A disciplina deve ser do mesmo curso da turma.'})
        if self.modulo_id and self.turma_id and self.modulo.curso_id != self.turma.curso_id:
            raise ValidationError({'modulo': 'O módulo deve pertencer ao mesmo curso da turma.'})
