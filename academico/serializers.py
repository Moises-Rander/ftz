from rest_framework import serializers

from .models import (
    Aula,
    Avaliacao,
    EntregaTrabalho,
    Frequencia,
    ResultadoAvaliacao,
    Trabalho,
)


def _nome_aluno(aluno):
    return aluno.user.get_full_name() or aluno.user.email


# ---------------------------------------------------------------------------
# Validação compartilhada de Disciplina/Módulo (Aula, Avaliação, Trabalho)
# ---------------------------------------------------------------------------


class _AtividadeValidatorMixin:
    def _validar_turma_disc_mod(self, attrs):
        instance = getattr(self, 'instance', None)

        def pick(field):
            return attrs.get(field, getattr(instance, field, None))

        turma = pick('turma')
        disciplina = pick('disciplina')
        modulo = pick('modulo')

        if bool(disciplina) == bool(modulo):
            raise serializers.ValidationError(
                'Preencha exatamente um entre Disciplina (Graduação) e Módulo (Formação).'
            )
        if disciplina is not None:
            if turma and not turma.curso.is_graduacao:
                raise serializers.ValidationError(
                    {'disciplina': 'Disciplina só se aplica a turmas de Graduação.'}
                )
            if turma and disciplina.curso_id != turma.curso_id:
                raise serializers.ValidationError(
                    {'disciplina': 'A disciplina deve pertencer ao curso da turma.'}
                )
        if modulo is not None:
            if turma and not turma.curso.is_formacao:
                raise serializers.ValidationError(
                    {'modulo': 'Módulo só se aplica a turmas de Formação.'}
                )
            if turma and modulo.curso_id != turma.curso_id:
                raise serializers.ValidationError(
                    {'modulo': 'O módulo deve pertencer ao curso da turma.'}
                )
        return turma, disciplina, modulo


# ---------------------------------------------------------------------------
# Admin — CRUD
# ---------------------------------------------------------------------------


class AulaAdminSerializer(_AtividadeValidatorMixin, serializers.ModelSerializer):
    class Meta:
        model = Aula
        fields = (
            'id', 'turma', 'disciplina', 'modulo', 'ciclo', 'data',
            'horario_inicio', 'duracao_minutos', 'cancelada', 'motivo_cancelamento',
        )

    def validate(self, attrs):
        turma, disciplina, modulo = self._validar_turma_disc_mod(attrs)
        instance = getattr(self, 'instance', None)
        ciclo = attrs.get('ciclo', getattr(instance, 'ciclo', None))

        if disciplina is not None:  # Graduação exige ciclo da mesma turma
            if ciclo is None:
                raise serializers.ValidationError(
                    {'ciclo': 'Aulas de Graduação devem referenciar um ciclo.'}
                )
            if turma and ciclo.turma_id != turma.id:
                raise serializers.ValidationError(
                    {'ciclo': 'O ciclo deve pertencer à turma da aula.'}
                )
        elif ciclo is not None:  # Formação não tem ciclo
            raise serializers.ValidationError(
                {'ciclo': 'Aulas de Formação não referenciam ciclo.'}
            )

        cancelada = attrs.get('cancelada', getattr(instance, 'cancelada', False))
        motivo = attrs.get('motivo_cancelamento', getattr(instance, 'motivo_cancelamento', None))
        if cancelada and not motivo:
            raise serializers.ValidationError(
                {'motivo_cancelamento': 'Informe o motivo ao cancelar a aula.'}
            )
        return attrs


class AvaliacaoAdminSerializer(_AtividadeValidatorMixin, serializers.ModelSerializer):
    class Meta:
        model = Avaliacao
        fields = (
            'id', 'turma', 'disciplina', 'modulo', 'titulo', 'descricao',
            'data', 'nota_maxima',
        )

    def validate(self, attrs):
        self._validar_turma_disc_mod(attrs)
        return attrs


class TrabalhoAdminSerializer(_AtividadeValidatorMixin, serializers.ModelSerializer):
    class Meta:
        model = Trabalho
        fields = (
            'id', 'turma', 'disciplina', 'modulo', 'titulo', 'descricao',
            'prazo_entrega', 'arquivo_enunciado',
        )

    def validate(self, attrs):
        self._validar_turma_disc_mod(attrs)
        return attrs


# ---------------------------------------------------------------------------
# Professor
# ---------------------------------------------------------------------------


class AulaProfessorSerializer(serializers.ModelSerializer):
    disciplina_nome = serializers.CharField(source='disciplina.nome', read_only=True, default=None)
    modulo_nome = serializers.CharField(source='modulo.nome', read_only=True, default=None)
    frequencia_lancada = serializers.SerializerMethodField()

    class Meta:
        model = Aula
        fields = (
            'id', 'turma', 'data', 'horario_inicio', 'duracao_minutos',
            'disciplina', 'disciplina_nome', 'modulo', 'modulo_nome',
            'cancelada', 'motivo_cancelamento', 'frequencia_lancada',
        )

    def get_frequencia_lancada(self, obj):
        return obj.frequencias.exists()


class FrequenciaItemSerializer(serializers.Serializer):
    aluno = serializers.IntegerField()
    presente = serializers.BooleanField()


class FrequenciaLoteSerializer(serializers.Serializer):
    itens = FrequenciaItemSerializer(many=True, allow_empty=False)


class FrequenciaSerializer(serializers.ModelSerializer):
    aluno_nome = serializers.SerializerMethodField()

    class Meta:
        model = Frequencia
        fields = ('id', 'aluno', 'aluno_nome', 'presente')

    def get_aluno_nome(self, obj):
        return _nome_aluno(obj.aluno)


class ResultadoItemSerializer(serializers.Serializer):
    aluno = serializers.IntegerField()
    nota = serializers.DecimalField(max_digits=5, decimal_places=2)


class ResultadoLoteSerializer(serializers.Serializer):
    itens = ResultadoItemSerializer(many=True, allow_empty=False)


class ResultadoSerializer(serializers.ModelSerializer):
    aluno_nome = serializers.SerializerMethodField()

    class Meta:
        model = ResultadoAvaliacao
        fields = ('id', 'aluno', 'aluno_nome', 'nota')

    def get_aluno_nome(self, obj):
        return _nome_aluno(obj.aluno)


class EntregaProfessorSerializer(serializers.ModelSerializer):
    aluno_nome = serializers.SerializerMethodField()

    class Meta:
        model = EntregaTrabalho
        fields = (
            'id', 'aluno', 'aluno_nome', 'arquivo', 'data_hora_entrega',
            'entregue_em_atraso', 'nota', 'feedback',
        )

    def get_aluno_nome(self, obj):
        return _nome_aluno(obj.aluno)


class CorrigirEntregaSerializer(serializers.Serializer):
    nota = serializers.DecimalField(max_digits=5, decimal_places=2, required=False, allow_null=True)
    feedback = serializers.CharField(required=False, allow_blank=True, allow_null=True)


# ---------------------------------------------------------------------------
# Aluno
# ---------------------------------------------------------------------------


class AulaAlunoSerializer(serializers.ModelSerializer):
    disciplina_nome = serializers.CharField(source='disciplina.nome', read_only=True, default=None)
    modulo_nome = serializers.CharField(source='modulo.nome', read_only=True, default=None)

    class Meta:
        model = Aula
        fields = (
            'id', 'data', 'horario_inicio', 'duracao_minutos',
            'disciplina_nome', 'modulo_nome', 'cancelada', 'motivo_cancelamento',
        )


class AvaliacaoAlunoSerializer(serializers.ModelSerializer):
    minha_nota = serializers.SerializerMethodField()

    class Meta:
        model = Avaliacao
        fields = ('id', 'titulo', 'descricao', 'data', 'nota_maxima', 'minha_nota')

    def get_minha_nota(self, obj):
        resultado = obj._resultado_aluno  # anexado pela view
        return str(resultado.nota) if resultado else 'não lançado'


class TrabalhoAlunoSerializer(serializers.ModelSerializer):
    status_entrega = serializers.SerializerMethodField()
    entregue_em_atraso = serializers.SerializerMethodField()
    nota = serializers.SerializerMethodField()
    feedback = serializers.SerializerMethodField()

    class Meta:
        model = Trabalho
        fields = (
            'id', 'titulo', 'descricao', 'prazo_entrega', 'arquivo_enunciado',
            'status_entrega', 'entregue_em_atraso', 'nota', 'feedback',
        )

    def get_status_entrega(self, obj):
        e = obj._entrega_aluno
        if e is None:
            return 'PENDENTE'
        return 'CORRIGIDO' if e.corrigida else 'ENTREGUE'

    def get_entregue_em_atraso(self, obj):
        return obj._entrega_aluno.entregue_em_atraso if obj._entrega_aluno else False

    def get_nota(self, obj):
        e = obj._entrega_aluno
        return str(e.nota) if e and e.nota is not None else None

    def get_feedback(self, obj):
        e = obj._entrega_aluno
        return e.feedback if e else None


class MinhaEntregaSerializer(serializers.ModelSerializer):
    status = serializers.SerializerMethodField()

    class Meta:
        model = EntregaTrabalho
        fields = (
            'id', 'trabalho', 'arquivo', 'data_hora_entrega',
            'entregue_em_atraso', 'nota', 'feedback', 'status',
        )

    def get_status(self, obj):
        return 'CORRIGIDO' if obj.corrigida else 'ENTREGUE'


class EntregaSubmitSerializer(serializers.Serializer):
    arquivo = serializers.FileField()
