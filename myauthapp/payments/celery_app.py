# Конфигурация Celery

from celery import Celery
from django.conf import settings

app = Celery('subscriptions')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()