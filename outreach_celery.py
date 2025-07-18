import os
from celery import Celery

# Set the default Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')

# Initialize Celery app
app = Celery('outreach_celery')

# Load settings from Django
app.config_from_object('django.conf:settings', namespace='CELERY')

# Automatically discover tasks from all installed apps
app.autodiscover_tasks()
