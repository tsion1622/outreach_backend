from __future__ import absolute_import, unicode_literals

# Ensures Celery app is loaded when Django starts
from .outreach_celery import app as celery_app

__all__ = ['celery_app']
