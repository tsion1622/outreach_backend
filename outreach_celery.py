import os
import ssl
from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")


app = Celery("outreach")


app.config_from_object("django.conf:settings", namespace="CELERY")


redis_url = os.getenv("REDIS_URL")
if redis_url:
    app.conf.broker_url = redis_url  

   
    if redis_url.startswith("rediss://"):
        ssl_opts = {"ssl_cert_reqs": ssl.CERT_NONE}
        app.conf.broker_use_ssl = ssl_opts
        app.conf.redis_backend_use_ssl = ssl_opts


app.autodiscover_tasks()
