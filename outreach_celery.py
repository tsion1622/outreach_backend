import os
import ssl
from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")  # or 'projectname.settings' if using project folder

app = Celery("outreach")
app.config_from_object("django.conf:settings", namespace="CELERY")

# Get Redis URL from env
redis_url = os.environ.get("REDIS_URL", "redis://localhost:6379/0")

# Set broker and backend
app.conf.broker_url = redis_url
app.conf.result_backend = redis_url

# SSL fix for rediss://
if redis_url.startswith("rediss://"):
    app.conf.broker_use_ssl = {"ssl_cert_reqs": ssl.CERT_NONE}
    app.conf.redis_backend_ssl = {"ssl_cert_reqs": ssl.CERT_NONE}

# Autodiscover tasks
app.autodiscover_tasks()
