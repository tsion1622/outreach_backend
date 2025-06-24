from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')  # adjust if needed

app = Celery('outreach')

# Load config from Django settings with 'CELERY_' namespace
app.config_from_object('django.conf:settings', namespace='CELERY')

# Use environment variable REDIS_URL for broker and backend
redis_url = os.getenv('REDIS_URL', 'redis://redis:6379/0')
app.conf.broker_url = redis_url
app.conf.result_backend = redis_url

# SSL options for Redis (important if REDIS_URL uses rediss://)
app.conf.broker_use_ssl = {
    'ssl_cert_reqs': False,  # or use ssl.CERT_NONE if you import ssl
}

app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
