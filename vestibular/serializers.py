from rest_framework import serializers

from .models import CandidatoVestibular, EdicaoVestibular


class EdicaoPublicaSerializer(serializers.ModelSerializer):
    """Edição para o site — NÃO expõe o prazo de matrícula pós-aprovação."""

    curso_nome = serializers.CharField(source='turma.curso.nome', read_only=True)
    turma_nome = serializers.CharField(source='turma.nome', read_only=True)
    inscricoes_abertas = serializers.SerializerMethodField()

    class Meta:
        model = EdicaoVestibular
        fields = (
            'id', 'curso_nome', 'turma_nome', 'data_prova', 'local_prova',
            'resultado_publicado', 'inscricoes_abertas',
        )

    def get_inscricoes_abertas(self, obj):
        # Aberto quando a turma está ABERTA e o resultado ainda não foi publicado.
        return obj.turma.status == 'ABERTA' and not obj.resultado_publicado


class InscricaoSerializer(serializers.Serializer):
    nome = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    cpf = serializers.CharField(max_length=14)
    telefone = serializers.CharField(max_length=20, required=False, allow_blank=True)


class ConsultaStatusSerializer(serializers.Serializer):
    cpf = serializers.CharField(max_length=14)


class CandidatoAdminSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = CandidatoVestibular
        fields = (
            'id', 'edicao', 'nome', 'cpf', 'email', 'telefone',
            'status', 'status_display', 'notificado_por_email',
        )
        read_only_fields = ('edicao', 'nome', 'cpf', 'email', 'telefone', 'notificado_por_email')


class CandidatoStatusUpdateSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=CandidatoVestibular.Status.choices)


class EdicaoAdminSerializer(serializers.ModelSerializer):
    # Contrato documentado usa "prazo_matricula_apos_aprovacao".
    prazo_matricula_apos_aprovacao = serializers.DateField(source='prazo_matricula')

    class Meta:
        model = EdicaoVestibular
        fields = (
            'id', 'turma', 'data_prova', 'local_prova',
            'prazo_matricula_apos_aprovacao', 'resultado_publicado', 'resultado_pdf',
        )
        # PDF e flag são geridos pela ação de publicação (somente leitura aqui).
        read_only_fields = ('resultado_publicado', 'resultado_pdf')

    def validate_turma(self, turma):
        if not turma.curso.is_graduacao:
            raise serializers.ValidationError(
                'O vestibular só se aplica a turmas de Graduação.'
            )
        return turma


class PublicarResultadoSerializer(serializers.Serializer):
    resultado_pdf = serializers.FileField()
