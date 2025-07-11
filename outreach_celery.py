from __future__ import absolute_import
import os
import django
import ssl
from celery import Celery

# 1. Set default Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')  # 👈 confirm if this is actually 'outreach_backend.settings'?

# 2. Setup Django
django.setup()

# 3. Create Celery app
app = Celery('outreach_celery')

# 4. Load config from Django settings
app.config_from_object('django.conf:settings', namespace='CELERY')

# 5. Redis SSL Fix for Upstash
app.conf.broker_use_ssl = {
    'ssl_cert_reqs': ssl.CERT_NONE
}
app.conf.result_backend_use_ssl = {
    'ssl_cert_reqs': ssl.CERT_NONE
}

# 6. Auto-discover tasks from installed apps
app.autodiscover_tasks()
