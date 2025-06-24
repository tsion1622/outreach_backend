from __future__ import absolute_import, unicode_literals
import os
import ssl
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')  # adjust if project has different module

app = Celery('outreach')

# Load settings from Django config
app.config_from_object('django.conf:settings', namespace='CELERY')

# Detect and apply SSL for rediss:// URLs
redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
app.conf.broker_url = redis_url
app.conf.result_backend = redis_url

if redis_url.startswith("rediss://"):
    app.conf.broker_use_ssl = {'ssl_cert_reqs': ssl.CERT_NONE}
    app.conf.redis_backend_use_ssl = {'ssl_cert_reqs': ssl.CERT_NONE}

# Auto-discover tasks in your apps
app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
