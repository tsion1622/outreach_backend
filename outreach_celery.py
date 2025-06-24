from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

# Set default Django settings module for 'celery'
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')  # adjust if needed

app = Celery('outreach')  # should match the Django project name

# Use os.getenv for environment variables
app.conf.broker_url = os.getenv('REDIS_URL', 'redis://redis:6379/0')
app.conf.result_backend = os.getenv('REDIS_URL', 'redis://redis:6379/0')

# Load configuration from Django settings with 'CELERY_' prefix
app.config_from_object('django.conf:settings', namespace='CELERY')

# Auto-discover tasks
app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
