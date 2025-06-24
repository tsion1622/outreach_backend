import os
import ssl
from celery import Celery

# Set the Django settings module environment variable
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")  # Change if settings are in a folder

app = Celery("outreach")

# Load celery settings from Django's settings.py using the "CELERY_" namespace
app.config_from_object("django.conf:settings", namespace="CELERY")

# Extra: SSL options for Upstash Redis
redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")

if redis_url.startswith("rediss://"):
    ssl_opts = {"ssl_cert_reqs": ssl.CERT_NONE}
    app.conf.broker_use_ssl = ssl_opts
    app.conf.redis_backend_ssl = ssl_opts

# Autodiscover tasks from Django apps
app.autodiscover_tasks()
