from __future__ import absolute_import
import os
import django
from celery import Celery

# 1. Set default Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'outreach_backend.settings')

# 2. Setup Django (MUST be done before importing models/tasks)
django.setup()

# 3. Create Celery app
app = Celery('outreach_backend')

# 4. Load Celery config from Django settings
app.config_from_object('django.conf:settings', namespace='CELERY')

# 5. Auto-discover tasks from installed apps
app.autodiscover_tasks()

# DO NOT manually import tasks like `import api.tasks` – not needed
