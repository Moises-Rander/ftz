from django.urls import reverse
from rest_framework import serializers

from cursos.models import Turma

from .models import Documento, Matricula


class MatriculaCreateSerializer(serializers.Serializer):
    """Entrada do início de matrícula (candidato anônimo)."""

    turma = serializers.PrimaryKeyRelatedField(queryset=Turma.objects.all())
    nome = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    cpf = serializers.CharField(max_length=14)
    telefone = serializers.CharField(max_length=20, required=False, allow_blank=True)
    data_nascimento = serializers.DateField(required=False, allow_null=True)
    metodo_pagamento = serializers.ChoiceField(choices=Matricula.MetodoPagamento.choices)
    codigo_cupom = serializers.CharField(required=False, allow_blank=True, default='')


class DocumentoSerializer(serializers.ModelSerializer):
    tipo_display = serializers.CharField(source='get_tipo_display', read_only=True)
    # NÃO expõe a URL crua do arquivo — apenas o endpoint de download autenticado.
    arquivo_url = serializers.SerializerMethodField()

    class Meta:
        model = Documento
        fields = ('id', 'tipo', 'tipo_display', 'arquivo_url', 'status')
        read_only_fields = ('status',)

    def get_arquivo_url(self, obj):
        if not obj.arquivo:
            return None
        url = reverse('matriculas:documento-download', args=[obj.id])
        request = self.context.get('request')
        return request.build_absolute_uri(url) if request else url


class TurmaResumoMatriculaSerializer(serializers.ModelSerializer):
    curso_nome = serializers.CharField(source='curso.nome', read_only=True)
    curso_tipo = serializers.CharField(source='curso.tipo', read_only=True)

    class Meta:
        model = Turma
        fields = ('id', 'nome', 'curso_nome', 'curso_tipo', 'status')


class MatriculaStatusSerializer(serializers.ModelSerializer):
    """Consulta de status pública (via token) — sem dados sensíveis demais."""

    status_display = serializers.CharField(source='get_status_display', read_only=True)
    turma = TurmaResumoMatriculaSerializer(read_only=True)
    documentos = DocumentoSerializer(many=True, read_only=True)

    class Meta:
        model = Matricula
        fields = (
            'id', 'status', 'status_display', 'turma', 'metodo_pagamento',
            'valor_final', 'url_pagamento', 'documentos', 'data_criacao',
        )


class MatriculaAlunoListSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    turma = TurmaResumoMatriculaSerializer(read_only=True)

    class Meta:
        model = Matricula
        fields = (
            'id', 'status', 'status_display', 'turma', 'valor_final', 'data_criacao',
        )


class MatriculaAlunoDetailSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    turma = TurmaResumoMatriculaSerializer(read_only=True)
    documentos = DocumentoSerializer(many=True, read_only=True)

    class Meta:
        model = Matricula
        fields = (
            'id', 'status', 'status_display', 'turma', 'metodo_pagamento',
            'valor_original', 'desconto_cupom', 'desconto_promocao', 'valor_final',
            'url_pagamento', 'documentos', 'motivo_rejeicao', 'data_criacao',
        )


class MatriculaAdminSerializer(serializers.ModelSerializer):
    """Detalhe completo para o Admin (inclui dados do candidato e documentos)."""

    status_display = serializers.CharField(source='get_status_display', read_only=True)
    turma = TurmaResumoMatriculaSerializer(read_only=True)
    documentos = DocumentoSerializer(many=True, read_only=True)
    aluno_email = serializers.SerializerMethodField()

    class Meta:
        model = Matricula
        fields = (
            'id', 'status', 'status_display', 'turma',
            'candidato_nome', 'candidato_email', 'candidato_cpf',
            'candidato_telefone', 'candidato_data_nascimento',
            'metodo_pagamento', 'valor_original', 'desconto_cupom',
            'desconto_promocao', 'valor_final', 'asaas_payment_id',
            'url_pagamento', 'documentos', 'motivo_rejeicao',
            'aluno', 'aluno_email', 'data_criacao',
        )

    def get_aluno_email(self, obj):
        return obj.aluno.user.email if obj.aluno_id else None
