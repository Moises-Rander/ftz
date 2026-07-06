import secrets
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone


def documento_storage():
    """Storage privado para documentos sensíveis (RG/CPF/histórico).

    Em S3, usa objetos privados (acesso só via URL assinada / view autenticada);
    em desenvolvimento, usa o storage local padrão (não servido publicamente
    fora do DEBUG). Chamável para não fixar o backend nas migrações.
    """
    from django.conf import settings
    if getattr(settings, 'USE_S3', False):
        from config.storages import PrivateMediaStorage
        return PrivateMediaStorage()
    from django.core.files.storage import default_storage
    return default_storage


class TipoDesconto(models.TextChoices):
    PERCENTUAL = 'PERCENTUAL', 'Percentual (%)'
    FIXO = 'FIXO', 'Valor fixo (R$)'


def _aplicar_desconto(valor_base, tipo, valor_desconto):
    """Retorna o valor do desconto (R$) sobre valor_base, sem nunca ultrapassá-lo."""
    valor_base = Decimal(valor_base)
    valor_desconto = Decimal(valor_desconto)
    if tipo == TipoDesconto.PERCENTUAL:
        desconto = valor_base * valor_desconto / Decimal('100')
    else:
        desconto = valor_desconto
    return min(desconto, valor_base).quantize(Decimal('0.01'))


class Cupom(models.Model):
    codigo = models.CharField('código', max_length=40, unique=True)
    tipo_desconto = models.CharField('tipo de desconto', max_length=12, choices=TipoDesconto.choices)
    valor_desconto = models.DecimalField('valor do desconto', max_digits=10, decimal_places=2)
    data_inicio = models.DateField('início da validade')
    data_fim = models.DateField('fim da validade')
    max_usos = models.PositiveIntegerField('máximo de usos', default=1)
    usos_atuais = models.PositiveIntegerField('usos atuais', default=0)
    is_ativo = models.BooleanField('ativo', default=True)
    curso = models.ForeignKey(
        'cursos.Curso', on_delete=models.CASCADE, null=True, blank=True,
        related_name='cupons', verbose_name='curso (opcional)',
    )

    class Meta:
        verbose_name = 'cupom'
        verbose_name_plural = 'cupons'
        ordering = ['codigo']

    def __str__(self):
        return self.codigo

    @property
    def esgotado(self):
        return self.usos_atuais >= self.max_usos

    def esta_valido(self, curso=None, em=None):
        """Impede uso quando vencido, desativado, esgotado ou de outro curso."""
        hoje = (em or timezone.localdate())
        if not self.is_ativo or self.esgotado:
            return False
        if not (self.data_inicio <= hoje <= self.data_fim):
            return False
        if self.curso_id and curso is not None and curso.pk != self.curso_id:
            return False
        return True

    def calcular_desconto(self, valor_base):
        return _aplicar_desconto(valor_base, self.tipo_desconto, self.valor_desconto)

    def clean(self):
        if self.data_inicio and self.data_fim and self.data_fim < self.data_inicio:
            raise ValidationError({'data_fim': 'A data de fim não pode ser anterior ao início.'})


class Promocao(models.Model):
    """Promoção vinculada a uma Turma OU a um Curso. Aplica-se automaticamente
    enquanto ativa e dentro do período de validade."""

    tipo_desconto = models.CharField('tipo de desconto', max_length=12, choices=TipoDesconto.choices)
    valor = models.DecimalField('valor do desconto', max_digits=10, decimal_places=2)
    data_inicio = models.DateField('início')
    data_fim = models.DateField('fim')
    is_ativa = models.BooleanField('ativa', default=True)
    turma = models.ForeignKey(
        'cursos.Turma', on_delete=models.CASCADE, null=True, blank=True,
        related_name='promocoes', verbose_name='turma',
    )
    curso = models.ForeignKey(
        'cursos.Curso', on_delete=models.CASCADE, null=True, blank=True,
        related_name='promocoes', verbose_name='curso',
    )

    class Meta:
        verbose_name = 'promoção'
        verbose_name_plural = 'promoções'
        ordering = ['-data_inicio']

    def __str__(self):
        alvo = self.turma or self.curso
        return f'Promoção {self.get_tipo_desconto_display()} — {alvo}'

    def esta_vigente(self, em=None):
        hoje = (em or timezone.localdate())
        return self.is_ativa and self.data_inicio <= hoje <= self.data_fim

    def calcular_desconto(self, valor_base):
        return _aplicar_desconto(valor_base, self.tipo_desconto, self.valor)

    def clean(self):
        if bool(self.turma_id) == bool(self.curso_id):
            raise ValidationError('Vincule a promoção a exatamente uma Turma OU um Curso.')
        if self.data_inicio and self.data_fim and self.data_fim < self.data_inicio:
            raise ValidationError({'data_fim': 'A data de fim não pode ser anterior ao início.'})


class Matricula(models.Model):
    class Status(models.TextChoices):
        AGUARDANDO_PAGAMENTO = 'AGUARDANDO_PAGAMENTO', 'Aguardando pagamento'
        AGUARDANDO_VALIDACAO = 'AGUARDANDO_VALIDACAO', 'Aguardando validação'
        APROVADA = 'APROVADA', 'Aprovada'
        REJEITADA = 'REJEITADA', 'Rejeitada'

    class MetodoPagamento(models.TextChoices):
        PIX = 'PIX', 'PIX'
        BOLETO = 'BOLETO', 'Boleto'
        CARTAO = 'CARTAO', 'Cartão'

    # O candidato é anônimo no início; a conta de Aluno só é criada na aprovação
    # (V4), então o vínculo com Aluno é preenchido apenas nesse momento.
    aluno = models.ForeignKey(
        'accounts.Aluno', on_delete=models.CASCADE, null=True, blank=True,
        related_name='matriculas', verbose_name='aluno',
    )
    turma = models.ForeignKey(
        'cursos.Turma', on_delete=models.CASCADE,
        related_name='matriculas', verbose_name='turma',
    )

    # Dados pessoais informados pelo candidato no início do processo.
    candidato_nome = models.CharField('nome do candidato', max_length=150)
    candidato_email = models.EmailField('email do candidato')
    candidato_cpf = models.CharField('CPF do candidato', max_length=14)
    candidato_telefone = models.CharField('telefone do candidato', max_length=20, blank=True)
    candidato_data_nascimento = models.DateField(
        'data de nascimento do candidato', null=True, blank=True
    )
    status = models.CharField(
        'status', max_length=24, choices=Status.choices, default=Status.AGUARDANDO_PAGAMENTO
    )
    metodo_pagamento = models.CharField(
        'método de pagamento', max_length=10, choices=MetodoPagamento.choices, blank=True
    )
    valor_original = models.DecimalField('valor original', max_digits=10, decimal_places=2)
    desconto_cupom = models.DecimalField(
        'desconto por cupom', max_digits=10, decimal_places=2, default=Decimal('0.00')
    )
    desconto_promocao = models.DecimalField(
        'desconto por promoção', max_digits=10, decimal_places=2, default=Decimal('0.00')
    )
    valor_final = models.DecimalField('valor final', max_digits=10, decimal_places=2)
    cupom = models.ForeignKey(
        Cupom, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='matriculas', verbose_name='cupom aplicado',
    )
    promocao = models.ForeignKey(
        Promocao, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='matriculas', verbose_name='promoção aplicada',
    )
    asaas_payment_id = models.CharField('ID do pagamento (Asaas)', max_length=120, blank=True)
    url_pagamento = models.URLField('URL do pagamento (boleto/QR PIX)', blank=True)
    # Token seguro para upload de documentos/consulta de status sem autenticação.
    upload_token = models.CharField(
        'token de upload', max_length=64, unique=True, db_index=True, editable=False
    )
    motivo_rejeicao = models.TextField('motivo da rejeição', blank=True)
    data_criacao = models.DateTimeField('criada em', auto_now_add=True)

    class Meta:
        verbose_name = 'matrícula'
        verbose_name_plural = 'matrículas'
        ordering = ['-data_criacao']
        constraints = [
            # Um aluno não pode ter duas matrículas APROVADAS na mesma turma.
            models.UniqueConstraint(
                fields=['aluno', 'turma'],
                condition=models.Q(status='APROVADA'),
                name='matricula_aprovada_unica_por_aluno_turma',
            ),
            # Idem por CPF do candidato (vínculo de Aluno só existe após aprovação).
            models.UniqueConstraint(
                fields=['candidato_cpf', 'turma'],
                condition=models.Q(status='APROVADA'),
                name='matricula_aprovada_unica_por_cpf_turma',
            ),
        ]

    def __str__(self):
        quem = self.aluno or self.candidato_nome
        return f'{quem} → {self.turma} [{self.get_status_display()}]'

    @property
    def ativa(self):
        return self.status != self.Status.REJEITADA

    @property
    def token_valido(self):
        """O token de upload expira quando a matrícula é APROVADA ou REJEITADA."""
        return self.status in (
            self.Status.AGUARDANDO_PAGAMENTO, self.Status.AGUARDANDO_VALIDACAO
        )

    @property
    def documentos_exigidos(self):
        """Tipos de documento exigidos conforme o tipo do curso da turma."""
        tipos = [Documento.Tipo.RG, Documento.Tipo.CPF]
        if self.turma.curso.is_graduacao:
            tipos.append(Documento.Tipo.HISTORICO_EM)
        return tipos

    def clean(self):
        # Impede duas matrículas ativas (não rejeitadas) do mesmo CPF na mesma turma.
        if self.candidato_cpf and self.turma_id:
            ativas = Matricula.objects.filter(
                candidato_cpf=self.candidato_cpf, turma=self.turma
            ).exclude(status=self.Status.REJEITADA).exclude(pk=self.pk)
            if ativas.exists():
                raise ValidationError('Já existe uma matrícula ativa para este CPF nesta turma.')

        # Ao aprovar, a turma precisa ter vaga disponível.
        if self.status == self.Status.APROVADA and self.turma_id:
            ocupadas = Matricula.objects.filter(
                turma=self.turma, status=self.Status.APROVADA
            ).exclude(pk=self.pk).count()
            if ocupadas >= self.turma.vagas_totais:
                raise ValidationError('A turma já atingiu o número de vagas totais.')

        if self.status == self.Status.REJEITADA and not self.motivo_rejeicao:
            raise ValidationError(
                {'motivo_rejeicao': 'Informe o motivo ao rejeitar a matrícula.'}
            )

    def save(self, *args, **kwargs):
        if not self.upload_token:
            self.upload_token = secrets.token_urlsafe(32)
        super().save(*args, **kwargs)
        # Mantém o status da turma (ABERTA/FECHADA) sincronizado com as vagas.
        self.turma.sincronizar_status_vagas()


class Documento(models.Model):
    class Tipo(models.TextChoices):
        RG = 'RG', 'RG'
        CPF = 'CPF', 'CPF'
        HISTORICO_EM = 'HISTORICO_EM', 'Histórico do Ensino Médio'

    class Status(models.TextChoices):
        PENDENTE = 'PENDENTE', 'Pendente'
        APROVADO = 'APROVADO', 'Aprovado'
        REJEITADO = 'REJEITADO', 'Rejeitado'

    matricula = models.ForeignKey(
        Matricula, on_delete=models.CASCADE, related_name='documentos', verbose_name='matrícula'
    )
    tipo = models.CharField('tipo', max_length=15, choices=Tipo.choices)
    arquivo = models.FileField('arquivo', upload_to='documentos/', storage=documento_storage)
    status = models.CharField(
        'status', max_length=10, choices=Status.choices, default=Status.PENDENTE
    )

    class Meta:
        verbose_name = 'documento'
        verbose_name_plural = 'documentos'

    def __str__(self):
        return f'{self.get_tipo_display()} — {self.matricula}'
