import tempfile
from datetime import date, timedelta
from decimal import Decimal

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from rest_framework.test import APIClient

from accounts.models import Aluno, User
from cursos.models import Curso, Turma, TipoCurso
from matriculas.models import Cupom, Documento, Matricula, Promocao
from matriculas.services import calcular_valores, processar_webhook, webhook_autentico


class DescontoTests(TestCase):
    def setUp(self):
        self.curso = Curso.objects.create(nome='C', tipo=TipoCurso.FORMACAO, preco_base=Decimal('200'))
        self.turma = Turma.objects.create(curso=self.curso, nome='T', vagas_totais=10, status='ABERTA')

    def test_promocao_e_cupom_somam_descontos(self):
        Promocao.objects.create(tipo_desconto='FIXO', valor=Decimal('20'), data_inicio=date.today() - timedelta(days=1), data_fim=date.today() + timedelta(days=10), is_ativa=True, curso=self.curso)
        cupom = Cupom.objects.create(codigo='DEZ', tipo_desconto='PERCENTUAL', valor_desconto=Decimal('10'), data_inicio=date.today() - timedelta(days=1), data_fim=date.today() + timedelta(days=10), max_usos=5, is_ativo=True)
        original, promo, cup, final, _ = calcular_valores(self.turma, cupom)
        self.assertEqual(original, Decimal('200.00'))
        self.assertEqual(promo, Decimal('20.00'))
        self.assertEqual(cup, Decimal('20.00'))  # 10% de 200
        self.assertEqual(final, Decimal('160.00'))

    def test_valor_final_nunca_negativo(self):
        cupom = Cupom.objects.create(codigo='TUDO', tipo_desconto='FIXO', valor_desconto=Decimal('999'), data_inicio=date.today() - timedelta(days=1), data_fim=date.today() + timedelta(days=10), max_usos=5, is_ativo=True)
        *_, final, _ = calcular_valores(self.turma, cupom)
        self.assertEqual(final, Decimal('0.00'))


class WebhookTests(TestCase):
    def setUp(self):
        curso = Curso.objects.create(nome='C', tipo=TipoCurso.FORMACAO, preco_base=Decimal('100'))
        self.turma = Turma.objects.create(curso=curso, nome='T', vagas_totais=10, status='ABERTA')
        self.matricula = Matricula.objects.create(
            turma=self.turma, candidato_nome='X', candidato_email='x@x.com', candidato_cpf='1',
            status='AGUARDANDO_PAGAMENTO', asaas_payment_id='pay_1',
            valor_original=Decimal('100'), valor_final=Decimal('100'),
        )

    def test_autenticacao_token(self):
        from django.test import override_settings
        with override_settings(ASAAS_WEBHOOK_TOKEN='segredo'):
            self.assertTrue(webhook_autentico({'asaas-access-token': 'segredo'}))
            self.assertFalse(webhook_autentico({'asaas-access-token': 'errado'}))
            self.assertFalse(webhook_autentico({}))

    def test_idempotente(self):
        payload = {'event': 'PAYMENT_CONFIRMED', 'payment': {'id': 'pay_1'}}
        r1 = processar_webhook(payload)
        self.assertTrue(r1.get('processed'))
        self.matricula.refresh_from_db()
        self.assertEqual(self.matricula.status, 'AGUARDANDO_VALIDACAO')
        # segunda vez: não reprocessa
        r2 = processar_webhook(payload)
        self.assertTrue(r2.get('ignored'))


@override_settings(MEDIA_ROOT=tempfile.mkdtemp())
class DocumentoDownloadTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        curso = Curso.objects.create(nome='C', tipo=TipoCurso.FORMACAO, preco_base=Decimal('100'))
        turma = Turma.objects.create(curso=curso, nome='T', vagas_totais=10, status='ABERTA')

        u = User.objects.create_user(email='dono@x.com', password='SenhaForte123', role=User.Role.ALUNO)
        self.aluno = Aluno.objects.create(user=u, cpf='1')
        self.matricula = Matricula.objects.create(
            turma=turma, aluno=self.aluno, candidato_nome='Dono', candidato_email='dono@x.com',
            candidato_cpf='1', status='APROVADA', valor_original=Decimal('100'), valor_final=Decimal('100'),
        )
        self.doc = Documento.objects.create(matricula=self.matricula, tipo='RG', arquivo=SimpleUploadedFile('rg.pdf', b'conteudo'))

        outro = User.objects.create_user(email='outro@x.com', password='SenhaForte123', role=User.Role.ALUNO)
        Aluno.objects.create(user=outro, cpf='2')
        self.admin = User.objects.create_superuser(email='adm@x.com', password='SenhaForte123')

    def _h(self, email):
        r = self.client.post('/api/auth/login/', {'email': email, 'password': 'SenhaForte123'}, format='json')
        return {'HTTP_AUTHORIZATION': f"Bearer {r.json()['access']}"}

    def _url(self):
        return f'/api/matriculas/documentos/{self.doc.id}/download/'

    def test_sem_auth_401(self):
        self.assertEqual(self.client.get(self._url()).status_code, 401)

    def test_outro_aluno_403(self):
        self.assertEqual(self.client.get(self._url(), **self._h('outro@x.com')).status_code, 403)

    def test_dono_baixa(self):
        self.assertEqual(self.client.get(self._url(), **self._h('dono@x.com')).status_code, 200)

    def test_admin_baixa(self):
        self.assertEqual(self.client.get(self._url(), **self._h('adm@x.com')).status_code, 200)
