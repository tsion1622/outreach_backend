import os
import ssl
from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")  # adjust if in subfolder

app = Celery("outreach")

# Load celery settings from Django settings.py
app.config_from_object("django.conf:settings", namespace="CELERY")

# Extra config for SSL Redis backend
redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")

if redis_url.startswith("rediss://"):
    app.conf.broker_use_ssl = {"ssl_cert_reqs": ssl.CERT_NONE}
    app.conf.redis_backend_ssl = {"ssl_cert_reqs": ssl.CERT_NONE}

# Discover tasks across Django apps
app.autodiscover_tasks()
