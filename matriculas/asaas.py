"""Cliente da integração com o Asaas.

Há duas implementações:
- ``AsaasClient``: chama a API real via HTTP (requests).
- ``FakeAsaasClient``: simula respostas, sem rede — usado quando
  ``settings.ASAAS_FAKE`` é True (desenvolvimento e testes).

``get_asaas_client()`` devolve a implementação adequada conforme o settings.
"""
import hashlib
import uuid

import requests
from django.conf import settings


class AsaasError(Exception):
    """Erro ao comunicar com o Asaas."""


# Mapeia o método de pagamento da FTZ para o billingType do Asaas.
BILLING_TYPE = {
    'PIX': 'PIX',
    'BOLETO': 'BOLETO',
    'CARTAO': 'CREDIT_CARD',
}


class AsaasClient:
    """Implementação real (HTTP) da API do Asaas."""

    def __init__(self, api_key=None, base_url=None):
        self.api_key = api_key or settings.ASAAS_API_KEY
        self.base_url = (base_url or settings.ASAAS_BASE_URL).rstrip('/')

    def _headers(self):
        return {'access_token': self.api_key, 'Content-Type': 'application/json'}

    def _post(self, path, payload):
        try:
            resp = requests.post(
                f'{self.base_url}{path}', json=payload,
                headers=self._headers(), timeout=20,
            )
            resp.raise_for_status()
            return resp.json()
        except requests.RequestException as exc:
            raise AsaasError(str(exc)) from exc

    def _get(self, path, params=None):
        try:
            resp = requests.get(
                f'{self.base_url}{path}', params=params,
                headers=self._headers(), timeout=20,
            )
            resp.raise_for_status()
            return resp.json()
        except requests.RequestException as exc:
            raise AsaasError(str(exc)) from exc

    def criar_ou_recuperar_cliente(self, *, nome, cpf, email, telefone=''):
        """Procura o cliente pelo CPF; cria se não existir. Retorna o id."""
        existentes = self._get('/customers', params={'cpfCnpj': cpf})
        data = existentes.get('data') or []
        if data:
            return data[0]['id']
        criado = self._post('/customers', {
            'name': nome, 'cpfCnpj': cpf, 'email': email, 'mobilePhone': telefone,
        })
        return criado['id']

    def criar_cobranca(self, *, customer_id, valor, metodo, descricao, referencia):
        cobranca = self._post('/payments', {
            'customer': customer_id,
            'billingType': BILLING_TYPE[metodo],
            'value': float(valor),
            'dueDate': _due_date(),
            'description': descricao,
            'externalReference': referencia,
        })
        return self._detalhar_pagamento(cobranca, metodo)

    def _detalhar_pagamento(self, cobranca, metodo):
        payment_id = cobranca['id']
        info = {'asaas_payment_id': payment_id, 'metodo': metodo}
        if metodo == 'PIX':
            qr = self._get(f'/payments/{payment_id}/pixQrCode')
            info['url_pagamento'] = cobranca.get('invoiceUrl', '')
            info['pix_qrcode_base64'] = qr.get('encodedImage', '')
            info['pix_copia_cola'] = qr.get('payload', '')
        elif metodo == 'BOLETO':
            info['url_pagamento'] = cobranca.get('bankSlipUrl', '')
            info['boleto_linha_digitavel'] = cobranca.get('identificationField', '')
        else:  # CARTAO
            info['url_pagamento'] = cobranca.get('invoiceUrl', '')
        return info


class FakeAsaasClient:
    """Cliente simulado (sem rede) — respostas determinísticas por CPF/método."""

    def criar_ou_recuperar_cliente(self, *, nome, cpf, email, telefone=''):
        digest = hashlib.sha1(cpf.encode()).hexdigest()[:12]
        return f'cus_fake_{digest}'

    def criar_cobranca(self, *, customer_id, valor, metodo, descricao, referencia):
        payment_id = f'pay_fake_{uuid.uuid4().hex[:16]}'
        info = {'asaas_payment_id': payment_id, 'metodo': metodo}
        base = f'https://sandbox.asaas.com/i/{payment_id}'
        if metodo == 'PIX':
            info['url_pagamento'] = base
            info['pix_qrcode_base64'] = 'iVBORw0KGgoFAKEQRCODEBASE64=='
            info['pix_copia_cola'] = f'00020126FAKE-PIX-{payment_id}'
        elif metodo == 'BOLETO':
            info['url_pagamento'] = f'{base}/boleto.pdf'
            info['boleto_linha_digitavel'] = '34191.79001 01043.510047 91020.150008 1 99990000010000'
        else:  # CARTAO
            info['url_pagamento'] = f'{base}/checkout'
        return info


def _due_date():
    from datetime import date, timedelta
    return (date.today() + timedelta(days=3)).isoformat()


def get_asaas_client():
    if getattr(settings, 'ASAAS_FAKE', False) or not settings.ASAAS_API_KEY:
        return FakeAsaasClient()
    return AsaasClient()
