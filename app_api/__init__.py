from __future__ import absolute_import, unicode_literals

# Isso garante que a aplicação Celery seja carregada sempre que o Django iniciar
from .celery import app as celery_app

__all__ = ('celery_app',)
