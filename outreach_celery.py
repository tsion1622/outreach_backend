from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from decouple import config

# Set default Django settings module for 'celery'
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')  # or 'outreach_backend.settings' if it's in a subfolder

app = Celery('outreach')  # App name should match project name, NOT the file name

# Broker and backend config
app.conf.broker_url = config('REDIS_URL', default='redis://redis:6379/0')
app.conf.result_backend = config('REDIS_URL', default='redis://redis:6379/0')

# Load config from Django settings, using CELERY_ prefix
app.config_from_object('django.conf:settings', namespace='CELERY')

# Discover tasks in all registered Django app configs
app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
