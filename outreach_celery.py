import os
import ssl
from celery import Celery

# Set Django settings module
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")  # or "yourproject.settings"

app = Celery("outreach")

# Load celery config from Django settings using "CELERY_" prefix
app.config_from_object("django.conf:settings", namespace="CELERY")

# Apply SSL config for Upstash Redis if rediss:// is used
redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
if redis_url.startswith("rediss://"):
    ssl_opts = {"ssl_cert_reqs": ssl.CERT_NONE}
    app.conf.broker_use_ssl = ssl_opts
    app.conf.redis_backend_ssl = ssl_opts

# Discover tasks automatically from all registered Django apps
app.autodiscover_tasks()
