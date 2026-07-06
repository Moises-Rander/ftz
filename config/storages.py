"""Backends de armazenamento em S3-compatível (ex.: Cloudflare R2, AWS S3).

Usados apenas quando ``settings.USE_S3`` é True.
- PublicMediaStorage: imagens públicas (logos, fotos, capas) — URL direta.
- PrivateMediaStorage: documentos sensíveis (RG/CPF/histórico) — objetos
  privados; servidos somente pela view autenticada de download.
"""
from storages.backends.s3boto3 import S3Boto3Storage


class PublicMediaStorage(S3Boto3Storage):
    location = 'media'
    default_acl = 'public-read'
    file_overwrite = False
    querystring_auth = False


class PrivateMediaStorage(S3Boto3Storage):
    location = 'private'
    default_acl = 'private'
    file_overwrite = False
    querystring_auth = True  # exige URL assinada para acesso direto
