"""Catálogo central de tipos de email da FTZ.

Cada tipo mapeia para um subject em português e um nome de template. Os
templates HTML e texto ficam em ``notifications/templates/notifications/`` com
os nomes ``<template>.html`` e ``<template>.txt``.
"""


class EmailType:
    # Conta e autenticação
    CONTA_DEFINIR_SENHA = 'CONTA_DEFINIR_SENHA'
    CONTA_RECUPERAR_SENHA = 'CONTA_RECUPERAR_SENHA'
    # Matrícula
    MATRICULA_INICIADA = 'MATRICULA_INICIADA'
    MATRICULA_PAGAMENTO_CONFIRMADO = 'MATRICULA_PAGAMENTO_CONFIRMADO'
    MATRICULA_AGUARDANDO_VALIDACAO = 'MATRICULA_AGUARDANDO_VALIDACAO'
    MATRICULA_APROVADA = 'MATRICULA_APROVADA'
    MATRICULA_REJEITADA = 'MATRICULA_REJEITADA'
    # Vestibular
    VESTIBULAR_INSCRICAO_CONFIRMADA = 'VESTIBULAR_INSCRICAO_CONFIRMADA'
    VESTIBULAR_RESULTADO_APROVADO = 'VESTIBULAR_RESULTADO_APROVADO'
    VESTIBULAR_RESULTADO_REPROVADO = 'VESTIBULAR_RESULTADO_REPROVADO'
    VESTIBULAR_RESULTADO_LISTA_ESPERA = 'VESTIBULAR_RESULTADO_LISTA_ESPERA'
    VESTIBULAR_PROMOVIDO_LISTA_ESPERA = 'VESTIBULAR_PROMOVIDO_LISTA_ESPERA'


# tipo -> (subject, nome do template)
REGISTRY = {
    EmailType.CONTA_DEFINIR_SENHA: (
        'Defina sua senha de acesso ao Portal FTZ', 'conta_definir_senha',
    ),
    EmailType.CONTA_RECUPERAR_SENHA: (
        'Redefinição de senha — FTZ', 'conta_recuperar_senha',
    ),
    EmailType.MATRICULA_INICIADA: (
        'Recebemos sua solicitação de matrícula — FTZ', 'matricula_iniciada',
    ),
    EmailType.MATRICULA_PAGAMENTO_CONFIRMADO: (
        'Pagamento confirmado — envie seus documentos — FTZ',
        'matricula_pagamento_confirmado',
    ),
    EmailType.MATRICULA_AGUARDANDO_VALIDACAO: (
        'Nova matrícula aguardando validação — FTZ', 'matricula_aguardando_validacao',
    ),
    EmailType.MATRICULA_APROVADA: (
        'Sua matrícula foi aprovada — FTZ', 'matricula_aprovada',
    ),
    EmailType.MATRICULA_REJEITADA: (
        'Sobre a sua matrícula — FTZ', 'matricula_rejeitada',
    ),
    EmailType.VESTIBULAR_INSCRICAO_CONFIRMADA: (
        'Inscrição no Vestibular confirmada — FTZ', 'vestibular_inscricao_confirmada',
    ),
    EmailType.VESTIBULAR_RESULTADO_APROVADO: (
        'Resultado do Vestibular — Faculdade de Teologia Zait',
        'vestibular_resultado_aprovado',
    ),
    EmailType.VESTIBULAR_RESULTADO_REPROVADO: (
        'Resultado do Vestibular — Faculdade de Teologia Zait',
        'vestibular_resultado_reprovado',
    ),
    EmailType.VESTIBULAR_RESULTADO_LISTA_ESPERA: (
        'Resultado do Vestibular — Faculdade de Teologia Zait',
        'vestibular_resultado_lista_espera',
    ),
    EmailType.VESTIBULAR_PROMOVIDO_LISTA_ESPERA: (
        'Você foi convocado da lista de espera — FTZ',
        'vestibular_promovido_lista_espera',
    ),
}
