"""Backends de armazenamento em S3-compatível (ex.: Cloudflare R2, AWS S3).

Usados apenas quando ``settings.USE_S3`` é True.

- PublicMediaStorage: imagens públicas (logos, fotos, capas) no bucket público.
- PrivateMediaStorage: documentos sensíveis (RG/CPF/histórico) em um bucket
  SEPARADO e privado — nunca exposto por URL pública; servidos apenas pela view
  autenticada de download.
"""
from django.conf import settings
from storages.backends.s3boto3 import S3Boto3Storage


class PublicMediaStorage(S3Boto3Storage):
    location = 'media'
    default_acl = None          # R2 não usa ACL; acesso público vem do domínio
    file_overwrite = False
    querystring_auth = False    # URLs públicas (via domínio público do bucket)


class PrivateMediaStorage(S3Boto3Storage):
    location = 'documentos'
    default_acl = None
    file_overwrite = False
    querystring_auth = True     # bucket privado; leitura via URL assinada/credencial

    def __init__(self, *args, **kwargs):
        # Bucket privado dedicado; se não configurado, cai no bucket padrão.
        priv = getattr(settings, 'AWS_PRIVATE_BUCKET_NAME', '') or settings.AWS_STORAGE_BUCKET_NAME
        kwargs.setdefault('bucket_name', priv)
        super().__init__(*args, **kwargs)
