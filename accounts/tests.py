from django.core.cache import cache
from django.test import TestCase
from rest_framework.test import APIClient

from accounts.models import Aluno, User


class AuthTests(TestCase):
    def setUp(self):
        cache.clear()  # zera contadores de throttle entre testes
        self.client = APIClient()
        self.user = User.objects.create_user(
            email='aluno@ftz.test', password='SenhaForte123',
            role=User.Role.ALUNO, first_name='Ana', last_name='Lima',
        )
        Aluno.objects.create(user=self.user, cpf='39053344705', telefone='11999990000')

    def test_login_ok_retorna_tokens_e_role(self):
        r = self.client.post('/api/auth/login/', {'email': 'aluno@ftz.test', 'password': 'SenhaForte123'}, format='json')
        self.assertEqual(r.status_code, 200)
        self.assertIn('access', r.json())
        self.assertIn('refresh', r.json())
        self.assertEqual(r.json()['user']['role'], 'ALUNO')

    def test_login_senha_errada_401(self):
        r = self.client.post('/api/auth/login/', {'email': 'aluno@ftz.test', 'password': 'errada'}, format='json')
        self.assertEqual(r.status_code, 401)

    def test_login_usuario_inativo_401(self):
        self.user.is_active = False
        self.user.save(update_fields=['is_active'])
        r = self.client.post('/api/auth/login/', {'email': 'aluno@ftz.test', 'password': 'SenhaForte123'}, format='json')
        self.assertEqual(r.status_code, 401)

    def _auth_header(self):
        r = self.client.post('/api/auth/login/', {'email': 'aluno@ftz.test', 'password': 'SenhaForte123'}, format='json')
        return {'HTTP_AUTHORIZATION': f"Bearer {r.json()['access']}"}

    def test_me_patch_ignora_role_e_atualiza_dados(self):
        h = self._auth_header()
        r = self.client.patch('/api/auth/me/', {'first_name': 'Aninha', 'telefone': '11888887777', 'role': 'ADMIN'}, format='json', **h)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json()['role'], 'ALUNO')  # role nunca muda por aqui
        self.assertEqual(r.json()['first_name'], 'Aninha')

    def test_change_password_fluxo(self):
        h = self._auth_header()
        # senha atual errada -> 400
        r = self.client.post('/api/auth/change-password/', {
            'old_password': 'errada', 'new_password': 'NovaSenha123', 'new_password_confirm': 'NovaSenha123',
        }, format='json', **h)
        self.assertEqual(r.status_code, 400)
        # troca correta -> 200
        r = self.client.post('/api/auth/change-password/', {
            'old_password': 'SenhaForte123', 'new_password': 'NovaSenha123', 'new_password_confirm': 'NovaSenha123',
        }, format='json', **h)
        self.assertEqual(r.status_code, 200)
        # nova senha funciona; antiga não
        self.assertEqual(self.client.post('/api/auth/login/', {'email': 'aluno@ftz.test', 'password': 'NovaSenha123'}, format='json').status_code, 200)
        self.assertEqual(self.client.post('/api/auth/login/', {'email': 'aluno@ftz.test', 'password': 'SenhaForte123'}, format='json').status_code, 401)
