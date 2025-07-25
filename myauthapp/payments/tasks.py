from celery import shared_task
from django.core.mail import send_mail
from django.utils import timezone
from .models import UserSubscription

@shared_task
def check_expiring_subscriptions():
    # Уведомление за 3 дня
    threshold = timezone.now() + timezone.timedelta(days=3)
    subscriptions = UserSubscription.objects.filter(
        end_date__lte=threshold,
        is_active=True
    )
    
    for sub in subscriptions:
        send_mail(
            "Ваша подписка скоро закончится",
            f"Подписка {sub.tariff.name} истекает {sub.end_date.strftime('%d.%m.%Y')}",
            "noreply@example.com",
            [sub.user.email],
            fail_silently=True,
        )