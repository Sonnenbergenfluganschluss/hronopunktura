from celery.schedules import crontab
from celery_app import app

app.conf.beat_schedule = {
    'check-subscriptions-daily': {
        'task': 'app.tasks.check_expiring_subscriptions',
        'schedule': crontab(hour=9, minute=0),  # Ежедневно в 9:00
    },
}