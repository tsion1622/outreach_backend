release: python manage.py migrate
web: ./start.sh
worker: celery -A outreach_celery worker --loglevel=info --concurrency=1 --pool=solo

