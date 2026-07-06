from django.utils.text import Truncator
from rest_framework import serializers

from .models import (
    AtribuicaoProfessor,
    Ciclo,
    Curso,
    Disciplina,
    GradeHoraria,
    HorarioFormacao,
    Modulo,
    ProgressoModuloTurma,
    Turma,
)

# ---------------------------------------------------------------------------
# Serializers públicos / de leitura
# ---------------------------------------------------------------------------


class CursoListSerializer(serializers.ModelSerializer):
    descricao_resumida = serializers.SerializerMethodField()
    tem_vagas_disponiveis = serializers.SerializerMethodField()

    class Meta:
        model = Curso
        fields = (
            'id', 'nome', 'descricao_resumida', 'tipo', 'carga_horaria',
            'imagem', 'tem_vagas_disponiveis',
        )

    def get_descricao_resumida(self, obj):
        return Truncator(obj.descricao or '').chars(160)

    def get_tem_vagas_disponiveis(self, obj):
        return any(
            t.status == Turma.Status.ABERTA and t.vagas_disponiveis > 0
            for t in obj.turmas.all()
        )


class DisciplinaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Disciplina
        fields = ('id', 'nome', 'descricao', 'ementa')


class ModuloSerializer(serializers.ModelSerializer):
    class Meta:
        model = Modulo
        fields = ('id', 'nome', 'descricao', 'ordem')


class TurmaResumoSerializer(serializers.ModelSerializer):
    vagas_disponiveis = serializers.IntegerField(read_only=True)

    class Meta:
        model = Turma
        fields = (
            'id', 'nome', 'status', 'vagas_totais', 'vagas_disponiveis',
            'prazo_matricula_pos_vestibular',
        )


class CursoDetailSerializer(serializers.ModelSerializer):
    disciplinas = serializers.SerializerMethodField()
    modulos = serializers.SerializerMethodField()
    turmas = serializers.SerializerMethodField()

    class Meta:
        model = Curso
        fields = (
            'id', 'nome', 'descricao', 'tipo', 'carga_horaria', 'preco_base',
            'imagem', 'disciplinas', 'modulos', 'turmas',
        )

    def get_disciplinas(self, obj):
        if not obj.is_graduacao:
            return None
        return DisciplinaSerializer(obj.disciplinas.all(), many=True).data

    def get_modulos(self, obj):
        if not obj.is_formacao:
            return None
        return ModuloSerializer(obj.modulos.all().order_by('ordem'), many=True).data

    def get_turmas(self, obj):
        # Público: turmas ENCERRADAS não aparecem.
        turmas = obj.turmas.exclude(status=Turma.Status.ENCERRADA)
        return TurmaResumoSerializer(turmas, many=True).data


class GradeHorariaSerializer(serializers.ModelSerializer):
    disciplina_nome = serializers.CharField(source='disciplina.nome', read_only=True)
    dia_semana_display = serializers.CharField(
        source='get_dia_semana_display', read_only=True
    )

    class Meta:
        model = GradeHoraria
        fields = (
            'id', 'disciplina', 'disciplina_nome', 'dia_semana',
            'dia_semana_display', 'horario', 'slots',
        )


class CicloSerializer(serializers.ModelSerializer):
    grades = GradeHorariaSerializer(many=True, read_only=True)

    class Meta:
        model = Ciclo
        fields = (
            'id', 'numero', 'data_inicio', 'data_fim', 'is_ativo', 'grades',
        )


class HorarioFormacaoSerializer(serializers.ModelSerializer):
    dia_1_display = serializers.CharField(source='get_dia_1_display', read_only=True)
    dia_2_display = serializers.CharField(source='get_dia_2_display', read_only=True)

    class Meta:
        model = HorarioFormacao
        fields = (
            'id', 'dia_1', 'dia_1_display', 'dia_2', 'dia_2_display',
            'horario_inicio', 'duracao_minutos',
        )


class ProgressoModuloSerializer(serializers.ModelSerializer):
    modulo = ModuloSerializer(read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = ProgressoModuloTurma
        fields = ('id', 'modulo', 'status', 'status_display', 'is_ativo')


class TurmaDetailSerializer(serializers.ModelSerializer):
    """Detalhe público da turma (informações divulgadas conforme regras)."""

    curso_tipo = serializers.CharField(source='curso.tipo', read_only=True)
    curso_nome = serializers.CharField(source='curso.nome', read_only=True)
    preco_base = serializers.DecimalField(
        source='curso.preco_base', max_digits=10, decimal_places=2, read_only=True
    )
    vagas_disponiveis = serializers.IntegerField(read_only=True)
    promocao = serializers.SerializerMethodField()
    ciclo_ativo = serializers.SerializerMethodField()
    horarios_formacao = serializers.SerializerMethodField()
    modulo_ativo = serializers.SerializerMethodField()

    class Meta:
        model = Turma
        fields = (
            'id', 'nome', 'curso', 'curso_nome', 'curso_tipo', 'status',
            'vagas_totais', 'vagas_disponiveis', 'preco_base', 'promocao',
            'prazo_matricula_pos_vestibular',
            'ciclo_ativo', 'horarios_formacao', 'modulo_ativo',
        )

    def get_promocao(self, obj):
        # Promoção vigente aplicável (turma/curso) — usada no resumo de matrícula.
        from matriculas.services import buscar_promocao_vigente
        promo = buscar_promocao_vigente(obj)
        if promo is None:
            return None
        return {
            'tipo_desconto': promo.tipo_desconto,
            'valor': str(promo.valor),
            'desconto': str(promo.calcular_desconto(obj.curso.preco_base)),
        }

    def get_ciclo_ativo(self, obj):
        if not obj.curso.is_graduacao:
            return None
        ciclo = obj.ciclos.filter(is_ativo=True).first()
        return CicloSerializer(ciclo).data if ciclo else None

    def get_horarios_formacao(self, obj):
        if not obj.curso.is_formacao:
            return None
        return HorarioFormacaoSerializer(obj.horarios_formacao.all(), many=True).data

    def get_modulo_ativo(self, obj):
        if not obj.curso.is_formacao:
            return None
        prog = obj.progressos_modulo.filter(is_ativo=True).select_related('modulo').first()
        return ModuloSerializer(prog.modulo).data if prog else None


class ProfessorAtribuidoSerializer(serializers.Serializer):
    """Professor atribuído à turma (dados públicos)."""

    id = serializers.IntegerField(source='professor.id', read_only=True)
    nome = serializers.SerializerMethodField()
    titulacao = serializers.CharField(source='professor.titulacao', read_only=True)
    foto = serializers.ImageField(source='professor.foto', read_only=True)

    def get_nome(self, obj):
        user = obj.professor.user
        return user.get_full_name() or user.email


class GradeCompletaSerializer(serializers.Serializer):
    """Grade completa da turma para o aluno matriculado / admin."""

    def to_representation(self, turma):
        if turma.curso.is_graduacao:
            ciclos = turma.ciclos.prefetch_related('grades__disciplina').order_by('numero')
            return {
                'tipo': turma.curso.tipo,
                'ciclos': CicloSerializer(ciclos, many=True).data,
            }
        progressos = turma.progressos_modulo.select_related('modulo').order_by('modulo__ordem')
        return {
            'tipo': turma.curso.tipo,
            'modulos': ProgressoModuloSerializer(progressos, many=True).data,
        }


# ---------------------------------------------------------------------------
# Serializers de gerenciamento (Admin)
# ---------------------------------------------------------------------------


class CursoAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = Curso
        fields = (
            'id', 'nome', 'descricao', 'imagem', 'tipo', 'carga_horaria', 'preco_base',
        )

    def validate_tipo(self, value):
        # Não pode alterar o tipo se já houver matrículas aprovadas em alguma turma.
        if self.instance and value != self.instance.tipo:
            tem_aprovadas = self.instance.turmas.filter(
                matriculas__status='APROVADA'
            ).exists()
            if tem_aprovadas:
                raise serializers.ValidationError(
                    'Não é possível alterar o tipo: já há matrículas aprovadas em turmas deste curso.'
                )
        return value


class TurmaAdminSerializer(serializers.ModelSerializer):
    vagas_ocupadas = serializers.IntegerField(read_only=True)
    vagas_disponiveis = serializers.IntegerField(read_only=True)

    class Meta:
        model = Turma
        fields = (
            'id', 'curso', 'nome', 'vagas_totais', 'status',
            'prazo_matricula_pos_vestibular', 'vagas_ocupadas', 'vagas_disponiveis',
        )

    def validate(self, attrs):
        curso = attrs.get('curso') or getattr(self.instance, 'curso', None)
        prazo = attrs.get('prazo_matricula_pos_vestibular',
                          getattr(self.instance, 'prazo_matricula_pos_vestibular', None))
        if prazo and curso and not curso.is_graduacao:
            raise serializers.ValidationError({
                'prazo_matricula_pos_vestibular':
                    'Prazo de matrícula pós-vestibular só se aplica a turmas de Graduação.'
            })

        # Reabertura: só permitida se as vagas não estiverem esgotadas.
        novo_status = attrs.get('status')
        if (self.instance and novo_status == Turma.Status.ABERTA
                and self.instance.status == Turma.Status.FECHADA
                and self.instance.lotada):
            raise serializers.ValidationError({
                'status': 'Não é possível reabrir: as vagas estão esgotadas.'
            })
        return attrs


class DisciplinaAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = Disciplina
        fields = ('id', 'curso', 'nome', 'descricao', 'ementa')

    def validate_curso(self, value):
        if not value.is_graduacao:
            raise serializers.ValidationError(
                'Disciplinas só podem ser vinculadas a cursos de Graduação.'
            )
        return value


class CicloAdminSerializer(serializers.ModelSerializer):
    grades = GradeHorariaSerializer(many=True, read_only=True)

    class Meta:
        model = Ciclo
        fields = (
            'id', 'turma', 'numero', 'data_inicio', 'data_fim', 'is_ativo', 'grades',
        )

    def validate(self, attrs):
        turma = attrs.get('turma') or getattr(self.instance, 'turma', None)
        if turma and not turma.curso.is_graduacao:
            raise serializers.ValidationError(
                {'turma': 'Ciclos só existem em turmas de Graduação.'}
            )
        inicio = attrs.get('data_inicio', getattr(self.instance, 'data_inicio', None))
        fim = attrs.get('data_fim', getattr(self.instance, 'data_fim', None))
        if inicio and fim and fim < inicio:
            raise serializers.ValidationError(
                {'data_fim': 'A data de fim não pode ser anterior ao início.'}
            )
        return attrs

    def create(self, validated_data):
        ativar = validated_data.pop('is_ativo', False)
        ciclo = Ciclo.objects.create(is_ativo=False, **validated_data)
        if ativar:
            ciclo.ativar()  # desativa os demais da turma
        return ciclo

    def update(self, instance, validated_data):
        ativar = validated_data.pop('is_ativo', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if ativar is True:
            instance.ativar()
        elif ativar is False and instance.is_ativo:
            instance.is_ativo = False
            instance.save(update_fields=['is_ativo'])
        return instance


class GradeHorariaAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = GradeHoraria
        fields = ('id', 'ciclo', 'disciplina', 'dia_semana', 'horario', 'slots')

    def validate(self, attrs):
        ciclo = attrs.get('ciclo') or getattr(self.instance, 'ciclo', None)
        disciplina = attrs.get('disciplina') or getattr(self.instance, 'disciplina', None)
        if ciclo and disciplina and disciplina.curso_id != ciclo.turma.curso_id:
            raise serializers.ValidationError(
                {'disciplina': 'A disciplina deve pertencer ao mesmo curso da turma do ciclo.'}
            )
        return attrs


class ModuloAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = Modulo
        fields = ('id', 'curso', 'nome', 'descricao', 'ordem')

    def validate_curso(self, value):
        if not value.is_formacao:
            raise serializers.ValidationError(
                'Módulos só podem ser vinculados a cursos de Formação.'
            )
        return value

    def validate(self, attrs):
        curso = attrs.get('curso') or getattr(self.instance, 'curso', None)
        ordem = attrs.get('ordem', getattr(self.instance, 'ordem', None))

        # ordem única por curso
        if curso and ordem is not None:
            conflito = Modulo.objects.filter(curso=curso, ordem=ordem)
            if self.instance:
                conflito = conflito.exclude(pk=self.instance.pk)
            if conflito.exists():
                raise serializers.ValidationError(
                    {'ordem': 'Já existe um módulo com esta ordem neste curso.'}
                )

        # não reordenar se algum módulo do curso já foi CONCLUÍDO em alguma turma
        if (self.instance and 'ordem' in attrs and attrs['ordem'] != self.instance.ordem):
            tem_concluido = ProgressoModuloTurma.objects.filter(
                modulo__curso=self.instance.curso,
                status=ProgressoModuloTurma.Status.CONCLUIDO,
            ).exists()
            if tem_concluido:
                raise serializers.ValidationError(
                    {'ordem': 'Não é possível reordenar: há módulos já concluídos em alguma turma.'}
                )
        return attrs


class ProgressoModuloTurmaAdminSerializer(serializers.ModelSerializer):
    # A ativação é feita pela ação dedicada (respeita a sequência); aqui é leitura.
    is_ativo = serializers.BooleanField(read_only=True)

    class Meta:
        model = ProgressoModuloTurma
        fields = ('id', 'turma', 'modulo', 'status', 'is_ativo')

    def validate(self, attrs):
        turma = attrs.get('turma') or getattr(self.instance, 'turma', None)
        modulo = attrs.get('modulo') or getattr(self.instance, 'modulo', None)
        if turma and not turma.curso.is_formacao:
            raise serializers.ValidationError(
                {'turma': 'Progresso de módulo só existe em turmas de Formação.'}
            )
        if turma and modulo and modulo.curso_id != turma.curso_id:
            raise serializers.ValidationError(
                {'modulo': 'O módulo deve pertencer ao mesmo curso da turma.'}
            )
        if attrs.get('status') == ProgressoModuloTurma.Status.ATIVO:
            raise serializers.ValidationError(
                {'status': 'Use a ação "ativar" para ativar um módulo (respeita a sequência).'}
            )
        return attrs


class HorarioFormacaoAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = HorarioFormacao
        fields = (
            'id', 'turma', 'dia_1', 'dia_2', 'horario_inicio', 'duracao_minutos',
        )

    def validate(self, attrs):
        turma = attrs.get('turma') or getattr(self.instance, 'turma', None)
        if turma and not turma.curso.is_formacao:
            raise serializers.ValidationError(
                {'turma': 'Horário de Formação só se aplica a turmas de Formação.'}
            )
        dia_1 = attrs.get('dia_1', getattr(self.instance, 'dia_1', None))
        dia_2 = attrs.get('dia_2', getattr(self.instance, 'dia_2', None))
        if dia_1 and dia_2 and dia_1 == dia_2:
            raise serializers.ValidationError(
                {'dia_2': 'Os dois dias da semana devem ser diferentes.'}
            )
        return attrs


class AtribuicaoProfessorAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = AtribuicaoProfessor
        fields = ('id', 'professor', 'turma', 'disciplina', 'modulo')

    def validate(self, attrs):
        def pick(field):
            return attrs.get(field, getattr(self.instance, field, None))

        professor = pick('professor')
        turma = pick('turma')
        disciplina = pick('disciplina')
        modulo = pick('modulo')

        # (2) obrigatoriamente disciplina OU módulo, nunca os dois
        if bool(disciplina) == bool(modulo):
            raise serializers.ValidationError(
                'Preencha exatamente um entre Disciplina (Graduação) e Módulo (Formação).'
            )
        # (1) disciplina/módulo pertencem ao curso da turma
        if disciplina and turma and disciplina.curso_id != turma.curso_id:
            raise serializers.ValidationError(
                {'disciplina': 'A disciplina deve pertencer ao curso da turma.'}
            )
        if modulo and turma and modulo.curso_id != turma.curso_id:
            raise serializers.ValidationError(
                {'modulo': 'O módulo deve pertencer ao curso da turma.'}
            )
        # (3) sem atribuição duplicada para o mesmo professor/turma/disciplina|módulo
        dup = AtribuicaoProfessor.objects.filter(
            professor=professor, turma=turma, disciplina=disciplina, modulo=modulo,
        )
        if self.instance:
            dup = dup.exclude(pk=self.instance.pk)
        if dup.exists():
            raise serializers.ValidationError('Esta atribuição já existe.')
        return attrs
